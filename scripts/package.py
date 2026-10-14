"""Bundle a PyInstaller onedir tree as a platform-specific, permission-safe ZIP."""
import sys
import zipfile
from pathlib import Path


def main():
    label=sys.argv[1] if len(sys.argv)>1 else 'Desktop'
    root=Path('dist/GlassBalance')
    if not root.is_dir():
        raise SystemExit('Run PyInstaller first (missing dist/GlassBalance).')
    target=Path(f'GlassBalance-{label}.zip')
    with zipfile.ZipFile(target,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=6) as archive:
        for file in sorted(root.rglob('*')):
            if not file.is_file():
                continue
            archive.write(file,arcname=file.relative_to(root.parent).as_posix())
        if label == 'Linux':
            source=Path('glassbalance/assets/glassbalance_icon.png')
            if not source.is_file():
                raise SystemExit('Missing packaged Linux icon asset')
            archive.write(source,arcname='glassbalance-icon.png')
            for script in ('install-linux.sh','uninstall-linux.sh'):
                archive.write(Path('scripts')/script,arcname=script)
    print(f'Packaged {target} ({target.stat().st_size:,} bytes)')


if __name__=='__main__':
    main()
