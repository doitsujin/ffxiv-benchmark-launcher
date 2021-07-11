#!/usr/bin/env python3

from configparser import ConfigParser

from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

import subprocess
import copy
import sys
import os

class FFXIVPreset:
  Maximum = 0
  HighDesktop = 1
  HighLaptop = 2
  StandardDesktop = 3
  StandardLaptop = 4

class FFXIVBenchmarkConfig:
  def __init__(self):
    self.cfg_path = os.getenv("XDG_CONFIG_HOME", os.getenv("HOME") + "/.config") + "/ffxiv_benchmark"
    self.cfg = ConfigParser()

    self.cfg["benchmark"] = {
      "path"                  : '' }

    wine_path = ""
    path_env = os.getenv("PATH")

    if (not path_env is None):
      for p in path_env.split(":"):
        probe_path = p + "/wine"

        if os.path.isfile(probe_path):
          wine_path = probe_path
          break

    self.cfg['wine'] = {
      "path"                  : wine_path,
      "prefix"                : os.getenv("HOME") + "/.wine",
      "environment"           : "WINEESYNC=1 WINEFSYNC=1 DXVK_LOG_LEVEL=none DXVK_HUD=fps,gpuload" }

    self.cfg['graphics'] = {
      "display_mode"          : "0",
      "display_res_x"         : "1280",
      "display_res_y"         : "720",
      "anti_aliasing"         : "True",
      "occlusion_culling"     : "False",
      "lod"                   : "False",
      "reflection"            : "0",
      "translucent"           : "0",
      "grass_quality"         : "0",
      "shadow_lod"            : "0",
      "shadow_self"           : "True",
      "shadow_other"          : "True",
      "shadow_resolution"     : "0",
      "shadow_cascading"      : "0",
      "shadow_soft"           : "0",
      "physics_self"          : "0",
      "physics_other"         : "0",
      "texture_filter"        : "0",
      "vignette"              : "True",
      "radial_blur"           : "True",
      "ssao"                  : "0",
      "glare_effect"          : "0",
      "depth_of_field"        : "True",
      "parallax_occlusion"    : "0",
      "tessellation"          : "0",
      "glare"                 : "0",
      "wet_surface"           : "True",
      "water_refraction"      : "0",
      "movement_self"         : "0",
      "movement_other"        : "0" }

    self.cfg.read(self.cfg_path)
    self.save()

  def save(self):
    with open(self.cfg_path, "w+") as f:
      self.cfg.write(f)

class FFXIVBenchmarkLauncher(QApplication):
  def __init__(self, args):
    super(FFXIVBenchmarkLauncher, self).__init__(args)
    self.text_benchmark_directory = QLineEdit()

    self.btn_benchmark_directory = QPushButton("Find")
    self.btn_benchmark_directory.clicked.connect(self.find_benchmark)

    layout_grid_launch_benchmark = QGridLayout()
    layout_grid_launch_benchmark.addWidget(QLabel("Directory:"), 0, 0)
    layout_grid_launch_benchmark.addWidget(self.text_benchmark_directory, 0, 1)
    layout_grid_launch_benchmark.addWidget(self.btn_benchmark_directory, 0, 2)

    group_launch_benchmark = QGroupBox("Benchmark")
    group_launch_benchmark.setLayout(layout_grid_launch_benchmark)

    self.text_wine_executable_path = QLineEdit()
    self.text_wine_prefix_path = QLineEdit()
    self.text_wine_environment = QLineEdit()

    self.btn_wine_executable_path = QPushButton("Find")
    self.btn_wine_executable_path.clicked.connect(self.find_wine)

    self.btn_wine_prefix_path = QPushButton("Find")
    self.btn_wine_prefix_path.clicked.connect(self.find_wine_prefix)

    layout_grid_launch_wine = QGridLayout()
    layout_grid_launch_wine.addWidget(QLabel("Executable:"), 0, 0)
    layout_grid_launch_wine.addWidget(self.text_wine_executable_path, 0, 1)
    layout_grid_launch_wine.addWidget(self.btn_wine_executable_path, 0, 2)
    layout_grid_launch_wine.addWidget(QLabel("Prefix:"), 1, 0)
    layout_grid_launch_wine.addWidget(self.text_wine_prefix_path, 1, 1)
    layout_grid_launch_wine.addWidget(self.btn_wine_prefix_path, 1, 2)
    layout_grid_launch_wine.addWidget(QLabel("Environment:"), 2, 0)
    layout_grid_launch_wine.addWidget(self.text_wine_environment, 2, 1, 1, 2)

    group_launch_wine = QGroupBox("Wine")
    group_launch_wine.setLayout(layout_grid_launch_wine)

    layout_vb_launch = QVBoxLayout()
    layout_vb_launch.addWidget(group_launch_benchmark)
    layout_vb_launch.addWidget(group_launch_wine)
    layout_vb_launch.addStretch()

    self.page_launch = QWidget()
    self.page_launch.setLayout(layout_vb_launch)

    btn_preset_max = QPushButton("Maximum")
    btn_preset_h_d = QPushButton("High (Desktop)")
    btn_preset_h_l = QPushButton("High (Laptop)")
    btn_preset_s_d = QPushButton("Standard (Desktop)")
    btn_preset_s_l = QPushButton("Standard (Laptop)")

    self.preset_buttons = [ btn_preset_max, btn_preset_h_d, btn_preset_h_l, btn_preset_s_d, btn_preset_s_l ]

    for p in self.preset_buttons:
      p.clicked.connect(self.apply_preset)

    layout_hb_graphics_preset = QHBoxLayout()
    layout_hb_graphics_preset.addWidget(btn_preset_max)
    layout_hb_graphics_preset.addWidget(btn_preset_h_d)
    layout_hb_graphics_preset.addWidget(btn_preset_h_l)
    layout_hb_graphics_preset.addWidget(btn_preset_s_d)
    layout_hb_graphics_preset.addWidget(btn_preset_s_l)

    group_graphics_preset = QGroupBox("Apply preset")
    group_graphics_preset.setLayout(layout_hb_graphics_preset)

    self.cb_fullscreen_mode = QComboBox()
    self.cb_fullscreen_mode.addItem("Windowed")
    self.cb_fullscreen_mode.addItem("Fullscreen")
    self.cb_fullscreen_mode.addItem("Borderless")

    layout_grid_display_mode = QGridLayout()
    layout_grid_display_mode.addWidget(QLabel("Mode:"), 0, 0)
    layout_grid_display_mode.addWidget(self.cb_fullscreen_mode, 0, 1, 1, 3)
    layout_grid_display_mode.setColumnStretch(0, 1)

    self.text_res_x = QLineEdit()
    self.text_res_x.setFixedWidth(60)

    self.text_res_y = QLineEdit()
    self.text_res_y.setFixedWidth(60)

    self.lbl_res = QLabel("Resolution:")
    self.lbl_res_x = QLabel("x")

    layout_grid_display_mode.addWidget(self.lbl_res, 1, 0)
    layout_grid_display_mode.addWidget(self.text_res_x, 1, 1)
    layout_grid_display_mode.addWidget(self.lbl_res_x, 1, 2)
    layout_grid_display_mode.addWidget(self.text_res_y, 1, 3)

    group_graphics_display = QGroupBox("Display mode")
    group_graphics_display.setLayout(layout_grid_display_mode)

    self.chk_fxaa = QCheckBox("Enable anti-aliasing")
    self.chk_occlusion_culling = QCheckBox("Enable occlusion culling")
    self.chk_distance_lod = QCheckBox("Use lower LOD for distant objects")

    self.cb_reflections = QComboBox()
    self.cb_reflections.addItem("Maximum")
    self.cb_reflections.addItem("High")
    self.cb_reflections.addItem("Normal")
    self.cb_reflections.addItem("Off")

    self.cb_transparent_lighting = QComboBox()
    self.cb_transparent_lighting.addItem("High")
    self.cb_transparent_lighting.addItem("Normal")

    self.cb_grass_quality = QComboBox()
    self.cb_grass_quality.addItem("High")
    self.cb_grass_quality.addItem("Normal")
    self.cb_grass_quality.addItem("Low")
    self.cb_grass_quality.addItem("Off")

    self.cb_parallax_occlusion = QComboBox()
    self.cb_parallax_occlusion.addItem("High")
    self.cb_parallax_occlusion.addItem("Standard")

    self.cb_tessellation = QComboBox()
    self.cb_tessellation.addItem("High")
    self.cb_tessellation.addItem("Standard")

    self.cb_glare = QComboBox()
    self.cb_glare.addItem("Standard")
    self.cb_glare.addItem("Off")

    self.cb_texture_filter = QComboBox()
    self.cb_texture_filter.addItem("16x Anisotropic")
    self.cb_texture_filter.addItem("8x Anisotropic")
    self.cb_texture_filter.addItem("4x Anisotropic")
    self.cb_texture_filter.addItem("Trilinear")

    layout_grid_graphics_general = QGridLayout()
    layout_grid_graphics_general.addWidget(self.chk_fxaa, 0, 0, 1, 2)
    layout_grid_graphics_general.addWidget(self.chk_occlusion_culling, 1, 0, 1, 2)
    layout_grid_graphics_general.addWidget(self.chk_distance_lod, 2, 0, 1, 2)
    layout_grid_graphics_general.addWidget(QLabel("Reflections:"), 3, 0)
    layout_grid_graphics_general.addWidget(self.cb_reflections, 3, 1)
    layout_grid_graphics_general.addWidget(QLabel("Transparent lighting:"), 4, 0)
    layout_grid_graphics_general.addWidget(self.cb_transparent_lighting, 4, 1)
    layout_grid_graphics_general.addWidget(QLabel("Grass quality:"), 5, 0)
    layout_grid_graphics_general.addWidget(self.cb_grass_quality, 5, 1)
    layout_grid_graphics_general.addWidget(QLabel("Parallax Occlusion:"), 6, 0)
    layout_grid_graphics_general.addWidget(self.cb_parallax_occlusion, 6, 1)
    layout_grid_graphics_general.addWidget(QLabel("Tessellation:"), 7, 0)
    layout_grid_graphics_general.addWidget(self.cb_tessellation, 7, 1)
    layout_grid_graphics_general.addWidget(QLabel("Glare:"), 8, 0)
    layout_grid_graphics_general.addWidget(self.cb_glare, 8, 1)
    layout_grid_graphics_general.addWidget(QLabel("Texture filter:"), 9, 0)
    layout_grid_graphics_general.addWidget(self.cb_texture_filter, 9, 1)

    group_graphics_general = QGroupBox("General")
    group_graphics_general.setLayout(layout_grid_graphics_general)

    self.chk_shadow_lod = QCheckBox("Use lower LOD for shadow rendering")
    self.chk_shadow_self = QCheckBox("Player character shadows")
    self.chk_shadow_npc = QCheckBox("Other character shadows")

    self.cb_shadow_resolution = QComboBox()
    self.cb_shadow_resolution.addItem("High (2048)")
    self.cb_shadow_resolution.addItem("Normal (1024)")
    self.cb_shadow_resolution.addItem("Low (512)")

    self.cb_shadow_cascading = QComboBox()
    self.cb_shadow_cascading.addItem("Best")
    self.cb_shadow_cascading.addItem("Normal")
    self.cb_shadow_cascading.addItem("Off")

    self.cb_shadow_softening = QComboBox()
    self.cb_shadow_softening.addItem("Strong")
    self.cb_shadow_softening.addItem("Weak")

    layout_grid_graphics_shadows = QGridLayout()
    layout_grid_graphics_shadows.addWidget(self.chk_shadow_lod, 0, 0, 1, 2)
    layout_grid_graphics_shadows.addWidget(self.chk_shadow_self, 1, 0)
    layout_grid_graphics_shadows.addWidget(self.chk_shadow_npc, 1, 1)
    layout_grid_graphics_shadows.addWidget(QLabel("Shadow resolution:"), 3, 0)
    layout_grid_graphics_shadows.addWidget(self.cb_shadow_resolution, 3, 1)
    layout_grid_graphics_shadows.addWidget(QLabel("Shadow cascades:"), 4, 0)
    layout_grid_graphics_shadows.addWidget(self.cb_shadow_cascading, 4, 1)
    layout_grid_graphics_shadows.addWidget(QLabel("Shadow softening:"), 5, 0)
    layout_grid_graphics_shadows.addWidget(self.cb_shadow_softening, 5, 1)

    group_graphics_shadows = QGroupBox("Shadows")
    group_graphics_shadows.setLayout(layout_grid_graphics_shadows)

    self.chk_wet_surface = QCheckBox("Wet surface effects")
    self.chk_vignette = QCheckBox("Vignette")
    self.chk_radial_blur = QCheckBox("Radial blur")
    self.chk_depth_of_field = QCheckBox("Depth of field")

    self.cb_ambient_occlusion = QComboBox()
    self.cb_ambient_occlusion.addItem("HBAO+ (Quality)")
    self.cb_ambient_occlusion.addItem("HBAO+ (Standard)")
    self.cb_ambient_occlusion.addItem("Strong")
    self.cb_ambient_occlusion.addItem("Weak")
    self.cb_ambient_occlusion.addItem("Off")

    self.cb_glare_effect = QComboBox()
    self.cb_glare_effect.addItem("Normal")
    self.cb_glare_effect.addItem("Low")
    self.cb_glare_effect.addItem("Off")

    self.cb_water_refraction = QComboBox()
    self.cb_water_refraction.addItem("Normal")
    self.cb_water_refraction.addItem("Low")
    self.cb_water_refraction.addItem("Off")

    layout_grid_graphics_effects = QGridLayout()
    layout_grid_graphics_effects.addWidget(self.chk_wet_surface, 0, 0)
    layout_grid_graphics_effects.addWidget(self.chk_vignette, 0, 1)
    layout_grid_graphics_effects.addWidget(self.chk_radial_blur, 1, 0)
    layout_grid_graphics_effects.addWidget(self.chk_depth_of_field, 1, 1)
    layout_grid_graphics_effects.addWidget(QLabel("Ambient occlusion:"), 2, 0)
    layout_grid_graphics_effects.addWidget(self.cb_ambient_occlusion, 2, 1)
    layout_grid_graphics_effects.addWidget(QLabel("Glare:"), 3, 0)
    layout_grid_graphics_effects.addWidget(self.cb_glare_effect, 3, 1)
    layout_grid_graphics_effects.addWidget(QLabel("Water refraction:"), 4, 0)
    layout_grid_graphics_effects.addWidget(self.cb_water_refraction, 4, 1)

    group_graphics_effects = QGroupBox("Effects")
    group_graphics_effects.setLayout(layout_grid_graphics_effects)

    rb_movement_self_full = QRadioButton("Full")
    rb_movement_self_simple = QRadioButton("Simple")
    rb_movement_self_off = QRadioButton("Off")

    rb_movement_npc_full = QRadioButton("Full")
    rb_movement_npc_simple = QRadioButton("Simple")
    rb_movement_npc_off = QRadioButton("Off")

    self.grp_movement_self = QButtonGroup()
    self.grp_movement_self.addButton(rb_movement_self_full, 0)
    self.grp_movement_self.addButton(rb_movement_self_simple, 1)
    self.grp_movement_self.addButton(rb_movement_self_off, 2)

    self.grp_movement_npc = QButtonGroup()
    self.grp_movement_npc.addButton(rb_movement_npc_full, 0)
    self.grp_movement_npc.addButton(rb_movement_npc_simple, 1)
    self.grp_movement_npc.addButton(rb_movement_npc_off, 2)

    layout_grid_graphics_movement = QGridLayout()
    layout_grid_graphics_movement.addWidget(QLabel("Player character:"), 0, 0)
    layout_grid_graphics_movement.addWidget(rb_movement_self_full, 0, 1)
    layout_grid_graphics_movement.addWidget(rb_movement_self_simple, 0, 2)
    layout_grid_graphics_movement.addWidget(rb_movement_self_off, 0, 3)
    layout_grid_graphics_movement.addWidget(QLabel("Other characters:"), 1, 0)
    layout_grid_graphics_movement.addWidget(rb_movement_npc_full, 1, 1)
    layout_grid_graphics_movement.addWidget(rb_movement_npc_simple, 1, 2)
    layout_grid_graphics_movement.addWidget(rb_movement_npc_off, 1, 3)

    group_graphics_movement = QGroupBox("Movement physics")
    group_graphics_movement.setLayout(layout_grid_graphics_movement)

    layout_vb_graphics_1 = QVBoxLayout()
    layout_vb_graphics_1.addWidget(group_graphics_display)
    layout_vb_graphics_1.addWidget(group_graphics_general)
    layout_vb_graphics_1.addStretch()

    layout_vb_graphics_2 = QVBoxLayout()
    layout_vb_graphics_2.addWidget(group_graphics_shadows)
    layout_vb_graphics_2.addWidget(group_graphics_effects)
    layout_vb_graphics_2.addWidget(group_graphics_movement)
    layout_vb_graphics_2.addStretch()

    layout_hb_graphics = QHBoxLayout()
    layout_hb_graphics.addLayout(layout_vb_graphics_1)
    layout_hb_graphics.addLayout(layout_vb_graphics_2)
    layout_hb_graphics.setStretch(0, 1)
    layout_hb_graphics.setStretch(1, 1)

    layout_vb_graphics = QVBoxLayout()
    layout_vb_graphics.addWidget(group_graphics_preset)
    layout_vb_graphics.addLayout(layout_hb_graphics)

    self.page_graphics = QWidget()
    self.page_graphics.setLayout(layout_vb_graphics)

    self.tab_widget = QTabWidget()
    self.tab_widget.addTab(self.page_launch, "Launch")
    self.tab_widget.addTab(self.page_graphics, "Graphics")

    self.btn_launch_char_creation = QPushButton("Character creation")
    self.btn_launch_char_creation.clicked.connect(self.launch_character_creation)

    self.btn_launch_benchmark = QPushButton("Start benchmark")
    self.btn_launch_benchmark.clicked.connect(self.launch_benchmark)

    layout_hb_buttons = QHBoxLayout()
    layout_hb_buttons.addStretch()
    layout_hb_buttons.addWidget(self.btn_launch_char_creation)
    layout_hb_buttons.addWidget(self.btn_launch_benchmark)

    layout_vb_window = QVBoxLayout()
    layout_vb_window.addWidget(self.tab_widget)
    layout_vb_window.addLayout(layout_hb_buttons)

    self.window = QWidget()
    self.window.setWindowTitle("FFXIV Benchmark Launcher")
    self.window.setLayout(layout_vb_window)
    self.window.show()

    self.config = FFXIVBenchmarkConfig()

    self.applyConfig(self.config.cfg)
    self.aboutToQuit.connect(self.on_quit)

  def applyConfig(self, cfg):
    self.text_benchmark_directory.setText(cfg.get("benchmark", "path"))
    self.text_wine_executable_path.setText(cfg.get("wine", "path"))
    self.text_wine_prefix_path.setText(cfg.get("wine", "prefix"))
    self.text_wine_environment.setText(cfg.get("wine", "environment"))
    self.cb_fullscreen_mode.setCurrentIndex(cfg.getint("graphics", "display_mode"))
    self.text_res_x.setText(str(cfg.getint("graphics", "display_res_x")))
    self.text_res_y.setText(str(cfg.getint("graphics", "display_res_y")))
    self.chk_fxaa.setChecked(cfg.getboolean("graphics", "anti_aliasing"))
    self.chk_occlusion_culling.setChecked(cfg.getboolean("graphics", "occlusion_culling"))
    self.chk_distance_lod.setChecked(cfg.getboolean("graphics", "lod"))
    self.cb_reflections.setCurrentIndex(cfg.getint("graphics", "reflection"))
    self.cb_transparent_lighting.setCurrentIndex(cfg.getint("graphics", "translucent"))
    self.cb_grass_quality.setCurrentIndex(cfg.getint("graphics", "grass_quality"))
    self.cb_parallax_occlusion.setCurrentIndex(cfg.getint("graphics", "parallax_occlusion"))
    self.cb_tessellation.setCurrentIndex(cfg.getint("graphics", "tessellation"))
    self.cb_glare.setCurrentIndex(cfg.getint("graphics", "glare"))
    self.cb_texture_filter.setCurrentIndex(cfg.getint("graphics", "texture_filter"))
    self.chk_shadow_lod.setChecked(cfg.getboolean("graphics", "shadow_lod"))
    self.chk_shadow_self.setChecked(cfg.getboolean("graphics", "shadow_self"))
    self.chk_shadow_npc.setChecked(cfg.getboolean("graphics", "shadow_other"))
    self.cb_shadow_resolution.setCurrentIndex(cfg.getint("graphics", "shadow_resolution"))
    self.cb_shadow_cascading.setCurrentIndex(cfg.getint("graphics", "shadow_cascading"))
    self.cb_shadow_softening.setCurrentIndex(cfg.getint("graphics", "shadow_soft"))
    self.chk_wet_surface.setChecked(cfg.getboolean("graphics", "wet_surface"))
    self.chk_vignette.setChecked(cfg.getboolean("graphics", "vignette"))
    self.chk_radial_blur.setChecked(cfg.getboolean("graphics", "radial_blur"))
    self.chk_depth_of_field.setChecked(cfg.getboolean("graphics", "depth_of_field"))
    self.cb_ambient_occlusion.setCurrentIndex(cfg.getint("graphics", "ssao"))
    self.cb_glare_effect.setCurrentIndex(cfg.getint("graphics", "glare_effect"))
    self.cb_water_refraction.setCurrentIndex(cfg.getint("graphics", "water_refraction"))

    movement_self_button = self.grp_movement_self.button(cfg.getint("graphics", "movement_self"))
    movement_npc_button = self.grp_movement_npc.button(cfg.getint("graphics", "movement_other"))

    if not movement_self_button is None:
      movement_self_button.setChecked(True)

    if not movement_npc_button is None:
      movement_npc_button.setChecked(True)

  def saveConfig(self, cfg):
    cfg.set("benchmark", "path", self.text_benchmark_directory.text())
    cfg.set("wine", "path", self.text_wine_executable_path.text())
    cfg.set("wine", "prefix", self.text_wine_prefix_path.text())
    cfg.set("wine", "environment", str(self.text_wine_environment.text()))
    cfg.set("graphics", "display_mode", str(self.cb_fullscreen_mode.currentIndex()))
    cfg.set("graphics", "display_res_x", self.text_res_x.text())
    cfg.set("graphics", "display_res_y", self.text_res_y.text())
    cfg.set("graphics", "anti_aliasing", str(self.chk_fxaa.isChecked()))
    cfg.set("graphics", "occlusion_culling", str(self.chk_occlusion_culling.isChecked()))
    cfg.set("graphics", "lod", str(self.chk_distance_lod.isChecked()))
    cfg.set("graphics", "reflection", str(self.cb_reflections.currentIndex()))
    cfg.set("graphics", "translucent", str(self.cb_transparent_lighting.currentIndex()))
    cfg.set("graphics", "grass_quality", str(self.cb_grass_quality.currentIndex()))
    cfg.set("graphics", "parallax_occlusion", str(self.cb_parallax_occlusion.currentIndex()))
    cfg.set("graphics", "tessellation", str(self.cb_tessellation.currentIndex()))
    cfg.set("graphics", "glare", str(self.cb_glare.currentIndex()))
    cfg.set("graphics", "texture_filter", str(self.cb_texture_filter.currentIndex()))
    cfg.set("graphics", "shadow_lod", str(self.chk_shadow_lod.isChecked()))
    cfg.set("graphics", "shadow_self", str(self.chk_shadow_self.isChecked()))
    cfg.set("graphics", "shadow_other", str(self.chk_shadow_npc.isChecked()))
    cfg.set("graphics", "shadow_resolution", str(self.cb_shadow_resolution.currentIndex()))
    cfg.set("graphics", "shadow_cascading", str(self.cb_shadow_cascading.currentIndex()))
    cfg.set("graphics", "shadow_soft", str(self.cb_shadow_softening.currentIndex()))
    cfg.set("graphics", "wet_surface", str(self.chk_wet_surface.isChecked()))
    cfg.set("graphics", "vignette", str(self.chk_vignette.isChecked()))
    cfg.set("graphics", "radial_blur", str(self.chk_radial_blur.isChecked()))
    cfg.set("graphics", "depth_of_field", str(self.chk_depth_of_field.isChecked()))
    cfg.set("graphics", "ssao", str(self.cb_ambient_occlusion.currentIndex()))
    cfg.set("graphics", "glare_effect", str(self.cb_glare_effect.currentIndex()))
    cfg.set("graphics", "water_refraction", str(self.cb_water_refraction.currentIndex()))
    cfg.set("graphics", "movement_self", str(self.grp_movement_self.checkedId()))
    cfg.set("graphics", "movement_other", str(self.grp_movement_npc.checkedId()))

  def apply_preset(self):
    preset = self.preset_buttons.index(self.window.sender())

    self.chk_wet_surface.setChecked(True)
    self.chk_shadow_self.setChecked(True)
    self.chk_radial_blur.setChecked(True)

    self.chk_occlusion_culling.setChecked(preset >= FFXIVPreset.HighDesktop)
    self.chk_distance_lod.setChecked(preset >= FFXIVPreset.HighLaptop)
    self.chk_shadow_lod.setChecked(preset >= FFXIVPreset.HighDesktop)
    self.chk_fxaa.setChecked(preset <= FFXIVPreset.HighLaptop)
    self.chk_shadow_npc.setChecked(preset <= FFXIVPreset.HighLaptop)
    self.chk_vignette.setChecked(preset <= FFXIVPreset.HighLaptop)
    self.grp_movement_self.button(0).setChecked(True)
    self.cb_glare_effect.setCurrentIndex(0)
    self.cb_water_refraction.setCurrentIndex(0)

    if preset <= FFXIVPreset.HighDesktop:
      self.cb_reflections.setCurrentIndex(0)
      self.cb_transparent_lighting.setCurrentIndex(0)
      self.cb_glare.setCurrentIndex(0)
      self.cb_shadow_resolution.setCurrentIndex(0)
    else:
      self.cb_reflections.setCurrentIndex(3)
      self.cb_transparent_lighting.setCurrentIndex(1)
      self.cb_glare.setCurrentIndex(1)
      self.cb_shadow_resolution.setCurrentIndex(1)

    if preset <= FFXIVPreset.HighLaptop:
      self.cb_tessellation.setCurrentIndex(0)
      self.cb_parallax_occlusion.setCurrentIndex(0)
      self.cb_shadow_cascading.setCurrentIndex(0)
      self.cb_shadow_softening.setCurrentIndex(0)
    else:
      self.cb_tessellation.setCurrentIndex(1)
      self.cb_parallax_occlusion.setCurrentIndex(1)
      self.cb_shadow_cascading.setCurrentIndex(1)
      self.cb_shadow_softening.setCurrentIndex(1)

    if preset < FFXIVPreset.HighLaptop:
      self.cb_grass_quality.setCurrentIndex(0)
    elif preset == FFXIVPreset.HighLaptop:
      self.cb_grass_quality.setCurrentIndex(1)
    elif preset > FFXIVPreset.HighLaptop:
      self.cb_grass_quality.setCurrentIndex(2)
    
    if preset == FFXIVPreset.Maximum:
      self.cb_texture_filter.setCurrentIndex(0)
    elif preset == FFXIVPreset.HighDesktop:
      self.cb_texture_filter.setCurrentIndex(1)
    elif preset == FFXIVPreset.HighLaptop:
      self.cb_texture_filter.setCurrentIndex(2)
    else:
      self.cb_texture_filter.setCurrentIndex(3)

    if preset == FFXIVPreset.Maximum:
      self.cb_ambient_occlusion.setCurrentIndex(0)
    elif preset <= FFXIVPreset.HighLaptop:
      self.cb_ambient_occlusion.setCurrentIndex(1)
    else:
      self.cb_ambient_occlusion.setCurrentIndex(4)

    if preset < FFXIVPreset.StandardDesktop:
      self.grp_movement_npc.button(0).setChecked(True)
    elif preset == FFXIVPreset.StandardDesktop:
      self.grp_movement_npc.button(1).setChecked(True)
    else:
      self.grp_movement_npc.button(2).setChecked(True)

  def find_benchmark(self):
    path = QFileDialog.getExistingDirectory(self.window, "Select benchmark directory")

    if not os.path.isfile(path + "/game/ffxiv_dx11.exe"):
      self.show_error(QMessageBox.Critical, "Benchmark executable (" + path + "/game/ffxiv_dx11.exe) not found.")
      return

    self.text_benchmark_directory.setText(path)

  def find_wine(self):
    (path, _) = QFileDialog.getOpenFileName(self.window, "Select Wine executable")
    self.text_wine_executable_path.setText(path)

  def find_wine_prefix(self):
    path = QFileDialog.getExistingDirectory(self.window, "Select Wine prefix")
    self.text_wine_prefix_path.setText(path)

  def launch_benchmark(self):
    self.launch(self.build_cmdline())

  def launch_character_creation(self):
    cmdline = self.build_cmdline()
    cmdline.append("Bench.CharacterCreation=1")
    self.launch(cmdline)

  def launch(self, cmdline):
    benchmark_dir = self.text_benchmark_directory.text()
    benchmark_exe_path = benchmark_dir + "/game/ffxiv_dx11.exe"
    wine_binary_path = self.text_wine_executable_path.text()
    wine_prefix_path = self.text_wine_prefix_path.text()

    if not os.path.isfile(benchmark_exe_path):
      self.show_error(QMessageBox.Critical, "Benchmark executable (" + benchmark_exe_path + ") not found.")
      return

    if not os.path.isfile(wine_binary_path):
      self.show_error(QMessageBox.Critical, "Wine executable (" + wine_binary_path + ") not found.")
      return

    if not os.path.isdir(wine_prefix_path):
      msg = QMessageBox()
      msg.setIcon(QMessageBox.Question)
      msg.setText("The given wine prefix does not exist. Continue anyway?")
      msg.setWindowTitle("Warning")
      msg.setStandardButtons(QMessageBox.Yes | QMessageBox.No)

      if msg.exec() == QMessageBox.No:
        return

    process_env = copy.deepcopy(os.environ)

    for e in self.text_wine_environment.text().split():
      v = e.split("=", 1)
      if len(v) == 2:
        process_env[v[0]] = v[1]

    cmdline.insert(0, wine_binary_path)
    cmdline.insert(1, benchmark_exe_path)

    ret = subprocess.run(cmdline, env=process_env, cwd=benchmark_dir)

    if ret.returncode != 0:
      self.show_error(QMessageBox.Warning, "Command execution failed with return code " + str(ret.returncode) + ".")

  def build_cmdline(self):
    texture_filter_type = 2
    texture_filter_anisotropy = 2

    if self.cb_texture_filter.currentIndex() >= 3:
      texture_filter_type = 1
    else:
      texture_filter_anisotropy = 2 - self.cb_texture_filter.currentIndex()

    cmd_args = [
      "SYS.Language=1", "SYS.Fps=0",
      "SYS.ScreenMode=" + str(self.cb_fullscreen_mode.currentIndex()),
      "SYS.ScreenWidth=" + self.text_res_x.text(),
      "SYS.ScreenHeight=" + self.text_res_y.text(),
      "SYS.FullScreenWidth=" + self.text_res_x.text(),
      "SYS.FullScreenHeight=" + self.text_res_y.text(),
      "SYS.WaterWet_DX11=" + str(int(self.chk_wet_surface.isChecked())),
      "SYS.OcclusionCulling_DX11=" + str(int(self.chk_occlusion_culling.isChecked())),
      "SYS.LodType_DX11=" + str(int(self.chk_distance_lod.isChecked())),
      "SYS.ReflectionType_DX11=" + str(3 - self.cb_reflections.currentIndex()),
      "SYS.AntiAliasing_DX11=" + str(int(self.chk_fxaa.isChecked())),
      "SYS.TranslucentQuality_DX11=" + str(1 - self.cb_transparent_lighting.currentIndex()),
      "SYS.GrassQuality_DX11=" + str(3 - self.cb_grass_quality.currentIndex()),
      "SYS.ShadowLOD_DX11=" + str(int(self.chk_shadow_lod.isChecked())),
      "SYS.ShadowVisibilityTypeSelf_DX11=" + str(int(self.chk_shadow_self.isChecked())),
      "SYS.ShadowVisibilityTypeOther_DX11=" + str(int(self.chk_shadow_npc.isChecked())),
      "SYS.ShadowTextureSizeType_DX11=" + str(2 - int(self.cb_shadow_resolution.currentIndex())),
      "SYS.ShadowCascadeCountType_DX11=" + str(2 - self.cb_shadow_cascading.currentIndex()),
      "SYS.ShadowSoftShadowType_DX11=" + str(1 - self.cb_shadow_softening.currentIndex()),
      "SYS.PhysicsTypeSelf_DX11=" + str(2 - self.grp_movement_self.checkedId()),
      "SYS.PhysicsTypeOther_DX11=" + str(2 - self.grp_movement_npc.checkedId()),
      "SYS.TextureFilterQuality_DX11=" + str(texture_filter_type),
      "SYS.TextureAnisotropicQuality_DX11=" + str(texture_filter_anisotropy),
      "SYS.Vignetting_DX11=" + str(int(self.chk_vignette.isChecked())),
      "SYS.RadialBlur_DX11=" + str(int(self.chk_radial_blur.isChecked())),
      "SYS.SSAO_DX11=" + str(4 - self.cb_ambient_occlusion.currentIndex()),
      "SYS.Glare_DX11=" + str(2 - self.cb_glare_effect.currentIndex()),
      "SYS.DepthOfField_DX11=" + str(int(self.chk_depth_of_field.isChecked())),
      "SYS.ParallaxOcclusion_DX11=" + str(1 - self.cb_parallax_occlusion.currentIndex()),
      "SYS.Tessellation_DX11=" + str(1 - self.cb_tessellation.currentIndex()),
      "SYS.GlareRepresentation_DX11=" + str(1 - self.cb_glare.currentIndex()),
      "SYS.DistortionWater_DX11=" + str(2 - self.cb_water_refraction.currentIndex()) ]

    return cmd_args

  def show_error(self, button, message):
    msg = QMessageBox()
    msg.setIcon(button)
    msg.setText(message)
    msg.setWindowTitle("Error")
    msg.setStandardButtons(QMessageBox.Ok)
    msg.exec()

  def on_quit(self):
    self.saveConfig(self.config.cfg)
    self.config.save()

if __name__ == "__main__":
  app = FFXIVBenchmarkLauncher(sys.argv)
  app.exec()
