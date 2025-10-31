import argparse
import os
import re
from pathlib import Path

from PIL import Image, ImageFile

ImageFile.LOAD_TRUNCATED_IMAGES = True

THUMBNAIL_ALIASES = {
    "hero_mobile": {"size": (640, 360), "quality": 80},
    "hero_mobile_2x": {"size": (1280, 720), "quality": 82},
    "hero_tablet": {"size": (1024, 576), "quality": 85},
    "hero_tablet_2x": {"size": (2048, 1152), "quality": 87},
    "hero_desktop": {"size": (1920, 1080), "quality": 90},
    "tour_card_mobile": {"size": (400, 280), "quality": 80},
    "tour_card_tablet": {"size": (600, 420), "quality": 85},
    "tour_card_desktop": {"size": (800, 560), "quality": 90},
    "tour_gallery_mobile": {"size": (480, 320), "quality": 80},
    "tour_gallery_tablet": {"size": (768, 512), "quality": 85},
    "tour_gallery_desktop": {"size": (1200, 800), "quality": 90},
    "blog_card_mobile": {"size": (400, 300), "quality": 80},
    "blog_card_tablet": {"size": (600, 450), "quality": 85},
    "blog_card_desktop": {"size": (800, 600), "quality": 90},
    "blog_hero_mobile": {"size": (640, 400), "quality": 80},
    "blog_hero_tablet": {"size": (1024, 640), "quality": 85},
    "blog_hero_desktop": {"size": (1920, 1200), "quality": 90},
}

SUPPORTED_FORMATS = {".jpg", ".jpeg", ".png", ".webp"}

# ------- Правила определения «уже сгенерированного» файла -------
# Совпадает, если ИМЯ БЕЗ РАСШИРЕНИЯ оканчивается на -mobile(-2x), -tablet(-2x), -desktop(-2x),
# а также -card(-2x), -gallery(-2x), -hero(-2x)
DERIVED_SUFFIX_RE = re.compile(
    r".*-(?:mobile|tablet|desktop|card|gallery|hero)(?:-2x)?$", re.IGNORECASE
)


def is_derived_file(filepath: Path) -> bool:
    """Является ли файл уже сгенерированной миниатюрой по нашему правилу нейминга."""
    return bool(DERIVED_SUFFIX_RE.match(filepath.stem))


def smart_crop_resize(
    img: Image.Image, target_width: int, target_height: int
) -> Image.Image:
    img_ratio = img.width / img.height
    target_ratio = target_width / target_height
    if img_ratio > target_ratio:
        new_width = int(img.height * target_ratio)
        left = (img.width - new_width) // 2
        img = img.crop((left, 0, left + new_width, img.height))
    else:
        new_height = int(img.width / target_ratio)
        top = (img.height - new_height) // 2
        img = img.crop((0, top, img.width, top + new_height))
    return img.resize((target_width, target_height), Image.Resampling.LANCZOS)


def alias_to_suffix(alias_name: str) -> str:
    parts = alias_name.split("_", 1)
    tail = parts[1] if len(parts) > 1 else alias_name
    if tail.endswith("_2x"):
        return tail[:-3] + "-2x"
    return tail


def pick_aliases_for_path(rel_dir: str) -> dict:
    rel = rel_dir.lower()
    if "hero" in rel:
        return {k: v for k, v in THUMBNAIL_ALIASES.items() if k.startswith("hero_")}
    if "tour" in rel:
        return {k: v for k, v in THUMBNAIL_ALIASES.items() if k.startswith("tour_")}
    if "blog" in rel:
        return {k: v for k, v in THUMBNAIL_ALIASES.items() if k.startswith("blog_")}
    return THUMBNAIL_ALIASES


def ensure_dir(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)


def will_be_generated_name(stem: str, alias_name: str) -> str:
    return f"{stem}-{alias_to_suffix(alias_name)}.webp"


def generate_thumbnails(source_path: Path, aliases: dict) -> None:
    """Генерация миниатюр для одного ОРИГИНАЛЬНОГО файла."""
    # Страховка: если вдруг сюда всё же попал derived — не генерим из него ничего.
    if is_derived_file(source_path):
        print(f"   🔒 Skip derived source: {source_path.name}")
        return

    stem = source_path.stem
    parent = source_path.parent

    try:
        with Image.open(source_path) as img:
            if img.mode in ("LA", "P"):
                img = img.convert("RGBA")

            for alias_name, config in aliases.items():
                width, height = config["size"]
                quality = int(config.get("quality", 80))

                out_name = will_be_generated_name(stem, alias_name)
                output = parent / out_name

                # Idempotency: если превью существует и свежее исходника — пропускаем
                if output.exists():
                    if output.stat().st_mtime >= source_path.stat().st_mtime:
                        print(f"   ⏭️  {output.name} (up-to-date)")
                        continue
                    else:
                        print(f"   ♻️  Rebuild {output.name} (source updated)")

                ensure_dir(output)
                thumb = smart_crop_resize(img.copy(), width, height)
                thumb.save(output, "WEBP", quality=quality, method=6)
                print(f"   ✅ {output.name} ({output.stat().st_size / 1024:.1f} KB)")

    except Exception as e:
        print(f"   ❌ Error: {source_path.name} -> {e}")


def find_static_img_dir(explicit: str | None) -> Path:
    if explicit:
        p = Path(explicit).expanduser().resolve()
        if not p.exists():
            raise SystemExit(f"Папка не найдена: {p}")
        return p

    candidates = [
        "core/static/img",
        "static/img",
        "backend/core/static/img",
        "app/core/static/img",
        "src/static/img",
    ]
    cwd = Path.cwd()
    for cand in candidates:
        p = (cwd / cand).resolve()
        if p.exists():
            return p

    raise SystemExit(
        "Не удалось найти папку с изображениями. "
        "Укажи путь явно: python generate_thumbs.py --src core/static/img"
    )


def main():
    parser = argparse.ArgumentParser(
        description="Generate WebP thumbnails (idempotent)"
    )
    parser.add_argument(
        "--src", help="Путь к папке с исходниками (например, core/static/img)"
    )
    args = parser.parse_args()

    static_img_dir = find_static_img_dir(args.src)
    print(f"🚀 Генерация миниатюр для: {static_img_dir}")
    print(f"📂 CWD: {Path.cwd()}\n")

    for root, _, files in os.walk(static_img_dir):
        root_path = Path(root)

        if any(
            skip in root_path.parts for skip in (".git", "__pycache__", "node_modules")
        ):
            continue

        # Берём только оригиналы: поддерживаемые форматы и НЕ подпадающие под наш шаблон "-mobile(-2x)" и т.п.
        image_files = []
        for f in files:
            p = root_path / f
            if p.suffix.lower() not in SUPPORTED_FORMATS:
                continue
            if is_derived_file(p):
                # отсекаем превью, чтобы не плодить цепочки
                continue
            image_files.append(f)

        if not image_files:
            continue

        rel = str(root_path.relative_to(static_img_dir)) or "."
        print(f"📁 {rel}/")
        aliases = pick_aliases_for_path(rel)

        for filename in sorted(image_files):
            source = root_path / filename
            print(f"  🖼️  {filename}")
            generate_thumbnails(source, aliases)
        print()

    print("✨ Готово!")


if __name__ == "__main__":
    main()
