#!/usr/bin/env -S PYTHONPATH=../../../tools/extract-utils python3
#
# SPDX-FileCopyrightText: The LineageOS Project
# SPDX-License-Identifier: Apache-2.0
#

from extract_utils.fixups_blob import (
    blob_fixup,
    blob_fixups_user_type,
)
from extract_utils.fixups_lib import (
    lib_fixups,
    lib_fixups_user_type,
)
from extract_utils.main import (
    ExtractUtils,
    ExtractUtilsModule,
)

namespace_imports = [
    'hardware/oplus',
    'hardware/qcom-caf/sm8650',
    'vendor/oneplus/sm8650-common',
    'vendor/qcom/opensource/commonsys-intf/display',
]

def lib_fixup_vendor_suffix(lib: str, partition: str, *args, **kwargs):
    return f'{lib}_{partition}' if partition == 'vendor' else None

lib_fixups: lib_fixups_user_type = {
    **lib_fixups,
    (
        'libarcsoft_triple_sat',
        'libarcsoft_triple_zoomtranslator',
        'libdualcam_optical_zoom_control',
        'libdualcam_video_optical_zoom',
        'libhwconfigurationutil',
        'libPanelChaplin',
        'libpwirisfeature',
        'libpwirishalwrapper',
        'libtriplecam_optical_zoom_control',
        'libtriplecam_video_optical_zoom',
        'vendor.oplus.hardware.displaycolorfeature-V1-ndk',
        'vendor.pixelworks.hardware.display@1.0',
        'vendor.pixelworks.hardware.display@1.1',
        'vendor.pixelworks.hardware.display@1.2',
        'vendor.pixelworks.hardware.feature@1.0',
        'vendor.pixelworks.hardware.feature@1.1',
    ): lib_fixup_vendor_suffix,
}

blob_fixups: blob_fixups_user_type = {
    'odm/lib64/libAlgoProcess.so': blob_fixup()
        .replace_needed('android.hardware.graphics.common-V3-ndk.so', 'android.hardware.graphics.common-V7-ndk.so')
        .replace_needed('android.hardware.graphics.common-V4-ndk.so', 'android.hardware.graphics.common-V7-ndk.so'),
    (
        'vendor/lib64/libpwirishalwrapper.so',
        'odm/lib64/libpwirishalwrapper.so',
    ): blob_fixup()
        .replace_needed(
            'android.hardware.graphics.composer3-V2-ndk.so',
            'android.hardware.graphics.composer3-V3-ndk.so',
        ),
    (
        'odm/lib64/libEIS.so',
        'odm/lib64/libEISLive.so',
        'odm/lib64/libHIS.so',
        'odm/lib64/libOGLManager.so',
        'odm/lib64/libOPAlgoCamAiBeautyFaceRetouchCn.so',
        'odm/lib64/libOPAlgoCamFaceBeautyCap.so',
    ): blob_fixup()
        .clear_symbol_version('AHardwareBuffer_acquire')
        .clear_symbol_version('AHardwareBuffer_allocate')
        .clear_symbol_version('AHardwareBuffer_describe')
        .clear_symbol_version('AHardwareBuffer_lock')
        .clear_symbol_version('AHardwareBuffer_lockPlanes')
        .clear_symbol_version('AHardwareBuffer_release')
        .clear_symbol_version('AHardwareBuffer_unlock'),
    'odm/lib64/libarcsoft_high_dynamic_range_v4.so': blob_fixup()
        .clear_symbol_version('remote_handle_close')
        .clear_symbol_version('remote_handle_invoke')
        .clear_symbol_version('remote_handle_open')
        .clear_symbol_version('remote_register_buf_attr')
        .clear_symbol_version('remote_register_buf'),
    (
        'odm/lib64/libCOppLceTonemapAPI.so',
        'odm/lib64/libSuperRaw.so',
        'odm/lib64/libYTCommon.so',
        'odm/lib64/libyuv2.so',
    ): blob_fixup()
        .replace_needed('libstdc++.so', 'libstdc++_vendor.so'),
    (
        'vendor/lib64/libcwb_qcom_aidl.so',
    ): blob_fixup()
        .add_needed('libui_shim.so'),
    (
        'vendor/lib64/libdpps.so',
        'vendor/lib64/libsnapdragoncolor-manager.so',
        'odm/lib64/libdisplaycolorfeature.so',
        'odm/lib64/libdisplayfossfeature_nature.so',
    ): blob_fixup()
        .replace_needed('libtinyxml2.so', 'libtinyxml2_stock.so'),
    'vendor/etc/libnfc-nci.conf': blob_fixup()
        .regex_replace('NFC_DEBUG_ENABLED=1', 'NFC_DEBUG_ENABLED=0'),
    'vendor/etc/libnfc-nxp.conf': blob_fixup()
        .regex_replace(r'(NXPLOG_\w+_LOGLEVEL[^\n]*?)0x03', r'\g<1>0x02')
        .regex_replace('NFC_DEBUG_ENABLED=1', 'NFC_DEBUG_ENABLED=0'),
    'odm/lib64/libImageWarpMask.so': blob_fixup()
        .fix_soname(),
    'odm/lib64/libBasicTonePhoto.so': blob_fixup()
        .binary_regex_replace(rb'vec4\(dstYuv\.r, dstYuv\.b, dstYuv\.g, 1\.0\)', b'vec4(dstYuv.r, dstYuv.g, dstYuv.b, 1.0)'),
    (
        'odm/lib64/libsharebuffer_impl.so',
    ): blob_fixup()
        .replace_needed('libui.so', 'libui-stock.so'),
    'vendor/lib64/libui-stock.so': blob_fixup()
        .replace_needed('android.hardware.graphics.common-V4-ndk.so', 'android.hardware.graphics.common-V7-ndk.so'),
}  # fmt: skip

module = ExtractUtilsModule(
    'giulia',
    'oneplus',
    namespace_imports=namespace_imports,
    blob_fixups=blob_fixups,
    lib_fixups=lib_fixups,
    add_firmware_proprietary_file=True,
)

if __name__ == '__main__':
    utils = ExtractUtils.device_with_common(module, 'sm8650-common', module.vendor)
    utils.run()
