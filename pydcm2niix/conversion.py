import os
import shutil
import subprocess
import tempfile
import dicom


def is_mt_on_philips(dicom_header):
    if 'philips' not in dicom_header.Manufacturer.lower():
        raise ValueError('Not a Philips header')
    private_mt_value = dicom_header.get([0x2005, 0x10a0]).value
    return private_mt_value > 0.0


def is_mt_on_toshiba(dicom_header, min_sar, max_sar):
    if 'toshiba' not in dicom_header.Manufacturer.lower():
        raise ValueError('Not a Toshiba header')
    sar_value = str(dicom_header.get((0x0018, 0x1316)).value)
    if (sar_value != min_sar) and (sar_value != max_sar):
        msg = 'SAR value is neither min nor max (val: {0!r}, min: {1!r}, max: {2!r})'.format(
            sar_value, min_sar, max_sar
        )
        raise ValueError(msg)
    return sar_value == max_sar


def is_mt_on_siemens(dicom_header):
    if 'siemens' not in dicom_header.Manufacturer.lower():
        raise ValueError('Not a Siemens header')
    scan_options = dicom_header.get('ScanOptions')
    return 'MT' in scan_options


def is_mt_on_hitachi(dicom_header):
    if 'hitachi' not in dicom_header.Manufacturer.lower():
        raise ValueError('Not a Hitachi header')
    sequence_variant = dicom_header.get('SequenceVariant')
    return 'MTC' in sequence_variant


def is_mt_on_ge(dicom_header):
    if 'ge' not in dicom_header.Manufacturer.lower():
        raise ValueError('Not a GE header')
    scan_options = dicom_header.get('ScanOptions')
    return 'MT_GEMS' in scan_options


def is_mt_on(dicom_header, min_sar=None, max_sar=None):
    manuf = dicom_header.Manufacturer.lower()
    if 'ge' in manuf:
        return is_mt_on_ge(dicom_header)
    elif 'philips' in manuf:
        return is_mt_on_philips(dicom_header)
    elif 'hitachi' in manuf:
        return is_mt_on_hitachi(dicom_header)
    elif 'siemens' in manuf:
        return is_mt_on_siemens(dicom_header)
    elif 'toshiba' in manuf:
        return is_mt_on_toshiba(dicom_header, min_sar, max_sar)


def convert_with_dcm2niix(dicom_dir, nifti_filename):
    if os.path.exists(nifti_filename):
        raise FileExistsError(nifti_filename)
    dirname = os.path.dirname(nifti_filename)
    filename = os.path.basename(nifti_filename)
    if filename.endswith('.nii.gz'):
        filename = filename[0:-7]
        compress = 'p'
    elif filename.endswith('.nii'):
        filename = filename[0:-4]
        compress = 'n'
    if dirname == '':
        dirname = '.'
    cmd = ['dcm2niix', '-z', compress, '-o', dirname, '-f', filename, dicom_dir]
    dcm2niix_output = subprocess.check_output(cmd)
    if b'warning' in dcm2niix_output.lower():
        print(dcm2niix_output)
        raise subprocess.CalledProcessError(0, cmd, dcm2niix_output)


def _sar_range(dicoms):
    sars = set([float(d.SAR) for d in dicoms])
    return str(min(sars)), str(max(sars))


def dicom_to_nifti_mt(dicom_dir, output_dir, mton_name='mton.nii.gz', mtoff_name='mtoff.nii.gz'):
    dicoms = []
    for f in os.listdir(dicom_dir):
        filename = os.path.join(dicom_dir, f)
        dicoms.append((filename, dicom.read_file(filename)))
    min_sar, max_sar = _sar_range((d[1] for d in dicoms))
    mton_dir = tempfile.mkdtemp(suffix='-mton')
    mtoff_dir = tempfile.mkdtemp(suffix='-mtoff')
    mt_found = [False, False]
    for filename, dicom_header in dicoms:
        if is_mt_on(dicom_header, min_sar=min_sar, max_sar=max_sar):
            shutil.copy(filename, mton_dir)
            mt_found[0] = True
        else:
            shutil.copy(filename, mtoff_dir)
            mt_found[1] = True
    if not all(mt_found):
        raise Exception('MT sequence detection failed ({0!r})'.format(dicom_dir))
    for mt_name, mt_dir in ((mton_name, mton_dir), (mtoff_name, mtoff_dir)):
        mt_filename = os.path.join(output_dir, mt_name)
        if os.path.exists(mt_filename):
            raise FileExistsError(mt_filename)
        convert_with_dcm2niix(mt_dir, mt_filename)
        shutil.rmtree(mt_dir)


def dicom_to_nifti(dicom_dir, output_dir, sequence):
    if sequence == 'mtr':
        dicom_to_nifti_mt(dicom_dir, output_dir)
    else:
        convert_with_dcm2niix(dicom_dir, os.path.join(output_dir, sequence + '.nii.gz'))
