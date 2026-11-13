#!/usr/bin/env -S PYTHONPATH=../../../tools/extract-utils python3
#
# SPDX-FileCopyrightText: 2024 The LineageOS Project
# SPDX-License-Identifier: Apache-2.0
#

from pathlib import Path
import sys

from extract_utils.fixups_blob import (
    blob_fixup,
    blob_fixups_user_type,
)
from extract_utils.fixups_lib import (
    lib_fixups,
)
from extract_utils.main import (
    ExtractUtils,
    ExtractUtilsModule,
)

sys.path.insert(
    0,
    str(
        Path(__file__).resolve().parents[1]
        / 'sm8450-common/sensors/sensor-notifier/udals'
    ),
)
from extract_model import fixup_model

UDALS_SPEC = {
    'sha256': 'f2522ec06f1ca53d3b58db70d645dfddd27b1e226ad4e2f075ad720cf752e0af',
    'grid': 25,
    'block_size': 5,
    'gamma': {'addr': 0x10ED98},
    'msg_unknown1': 1,
    'sensor_owner': 'sns_tmd3719',
    'spatial': [0x113290, 0x113290, 0x113290],
    'input_transform': 'log',
    'routing': 'dbv_rules',
    'dc_curve_max_dbv': 400,
    'networks': [
        {
            'max_dbv': 400,
            'dc': False,
            'base': 0x177F18,
            'layers': [128, 64, 32, 4],
            'output_bias': [
                {'addr': 0x10EE18},
                {'addr': 0x10EE38},
                {'addr': 0x10EDF8},
                {'addr': 0x10ED90},
            ],
            'exponent': [
                {'addr': 0x10EDC0},
                {'addr': 0x10EDA8},
                {'addr': 0x10EE10},
                {'addr': 0x10EE50},
            ],
            'negative': 'clamp',
        },
        {
            'max_dbv': 400,
            'dc': True,
            'base': 0x162418,
            'layers': [128, 64, 32, 4],
            'output_bias': [
                {'addr': 0x10ED88},
                {'addr': 0x10ED60},
                {'addr': 0x10EDF0},
                {'addr': 0x10ED70},
            ],
            'exponent': [
                {'addr': 0x10EDC0},
                {'addr': 0x10EDA8},
                {'addr': 0x10EE10},
                {'addr': 0x10EE30},
            ],
            'negative': 'zero',
        },
        {
            'max_dbv': 900,
            'base': 0x114618,
            'layers': [256, 64, 32, 4],
            'output_bias': [
                {'addr': 0x10EDD8},
                {'addr': 0x10EE00},
                {'addr': 0x10ED50},
                {'addr': 0x10EDE0},
            ],
            'exponent': [
                {'addr': 0x10EDE8},
                {'addr': 0x10EDA0},
                {'addr': 0x10EE58},
                {'addr': 0x10ED68},
            ],
            'negative': 'zero',
        },
        {
            'base': 0x13B518,
            'layers': [256, 64, 32, 4],
            'output_bias': [
                {'addr': 0x10EE20},
                {'addr': 0x10EE60},
                {'addr': 0x10ED58},
                {'addr': 0x10ED78},
            ],
            'exponent': [
                4.05,
                {'addr': 0x10EE48},
                {'addr': 0x10EE08},
                {'addr': 0x10ED80},
            ],
            'negative': 'zero',
        },
    ],
    'lux': {
        'coef_scale': False,
        'divisor': 1.0,
        'dbv_offset_above': 1700,
        'dbv_offset': 20.0,
        'low_lux_threshold': 30.0,
        'low_lux_offset': -2.0,
    },
    'filter': {
        'low_lux_window': 7,
        'median_window': 5,
        'truncate_median_to_int': True,
        'deadband_strict_less': False,
        'deadband_tiers': [
            {'below': 10.0, 'ratio': {'addr': 0x10EE68}},
            {'below': 30.0, 'ratio': {'addr': 0x10EDD0}},
            {'below': 60.0, 'ratio': 0.3},
            {'ratio': {'addr': 0x10EE28}},
        ],
    },
}

namespace_imports = [
    'device/xiaomi/sm8450-common',
    'hardware/qcom-caf/sm8450',
    'hardware/xiaomi',
    'vendor/qcom/opensource/commonsys-intf/display',
    'vendor/xiaomi/sm8450-common',
]

blob_fixups: blob_fixups_user_type = {
    'vendor/lib64/hw/camera.qcom.so': blob_fixup()
        .add_needed('libcamximageformatutils_shim.so'),
    (
        'vendor/etc/camera/mayfly_enhance_motiontuning.xml',
        'vendor/etc/camera/mayfly_motiontuning.xml',
    ): blob_fixup().regex_replace('xml=version', 'xml version'),
    'vendor/etc/camera/pureView_parameter.xml': blob_fixup().regex_replace(
        r'=([0-9]+)>', r'="\1">'
    ),
    'vendor/etc/sensors/udals-model.json': blob_fixup().call(
        fixup_model, UDALS_SPEC
    ),
    (
        'vendor/lib64/camera/plugins/com.xiaomi.plugin.mialgosnsc.so',
        'vendor/lib64/com.qti.feature2.anchorsync.so',
    ): blob_fixup().replace_needed('libtinyxml2.so', 'libtinyxml2-v34.so'),
    (
        'vendor/lib64/hw/com.qti.chi.override.so',
        'vendor/lib64/libcamxcommonutils.so',
        'vendor/lib64/libmialgoengine.so',
    ): blob_fixup().add_needed('libprocessgroup_shim.so'),
    (
        'vendor/lib64/libMiVideoFilter.so',
        'vendor/lib64/libTrueSight.so',
    ): blob_fixup()
    .clear_symbol_version('AHardwareBuffer_allocate')
    .clear_symbol_version('AHardwareBuffer_describe')
    .clear_symbol_version('AHardwareBuffer_lock')
    .clear_symbol_version('AHardwareBuffer_lockPlanes')
    .clear_symbol_version('AHardwareBuffer_release')
    .clear_symbol_version('AHardwareBuffer_unlock'),
}

module = ExtractUtilsModule(
    'mayfly',
    'xiaomi',
    blob_fixups=blob_fixups,
    lib_fixups=lib_fixups,
    namespace_imports=namespace_imports,
    add_firmware_proprietary_file=True,
)

if __name__ == '__main__':
    utils = ExtractUtils.device_with_common(
        module, 'sm8450-common', module.vendor
    )
    utils.run()
