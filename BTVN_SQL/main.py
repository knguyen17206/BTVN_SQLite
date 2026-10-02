import sqlite3
import time
import random
import re

from urllib.parse import urljoin, urlparse

from playwright.sync_api import (
    sync_playwright,
    TimeoutError as PWTimeout
)


# =========================================================
# CẤU HÌNH
# =========================================================

BASE_URL = "https://www.thegioididong.com"

DATABASE_NAME = "thegioididong.db"

HEADLESS = False

PAGE_LOAD_TIMEOUT = 60000

DELAY_MIN = 1.0
DELAY_MAX = 2.5

# None = KHÔNG GIỚI HẠN
MAX_PRODUCTS = None


# =========================================================
# CÁC TRANG DANH MỤC CHÍNH
# =========================================================

CATEGORY_URLS = {

    "Điện thoại":
        f"{BASE_URL}/dtdd",

    "Laptop":
        f"{BASE_URL}/laptop",

    "Máy tính bảng":
        f"{BASE_URL}/may-tinh-bang",

    "Đồng hồ thông minh":
        f"{BASE_URL}/dong-ho-thong-minh",

    "Đồng hồ":
        f"{BASE_URL}/dong-ho-deo-tay",

    "Phụ kiện":
        f"{BASE_URL}/phu-kien",

    "PC - Máy in":
        f"{BASE_URL}/pc-may-in"
}


# =========================================================
# DATABASE
# =========================================================

def connect_db():

    return sqlite3.connect(
        DATABASE_NAME
    )


def create_table():

    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS Product (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            url TEXT NOT NULL UNIQUE,

            name TEXT NOT NULL,

            category TEXT,

            price TEXT,

            old_price TEXT,

            discount TEXT,

            rating TEXT,

            sold TEXT,

            image TEXT,

            error TEXT

        )
    """)

    conn.commit()
    conn.close()


# =========================================================
# LƯU NGAY VÀO DATABASE
# =========================================================

def save_product(product):

    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO Product
        (
            url,
            name,
            category,
            price,
            old_price,
            discount,
            rating,
            sold,
            image,
            error
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)

        ON CONFLICT(url)
        DO UPDATE SET

            name = excluded.name,
            category = excluded.category,
            price = excluded.price,
            old_price = excluded.old_price,
            discount = excluded.discount,
            rating = excluded.rating,
            sold = excluded.sold,
            image = excluded.image,
            error = excluded.error
    """, (

        product.get("url", ""),

        product.get("name", ""),

        product.get("category", ""),

        product.get("price", ""),

        product.get("old_price", ""),

        product.get("discount", ""),

        product.get("rating", ""),

        product.get("sold", ""),

        product.get("image", ""),

        product.get("error", "")
    ))

    # QUAN TRỌNG:
    # GHI NGAY XUỐNG DATABASE
    conn.commit()

    conn.close()


# =========================================================
# HÀM LẤY TEXT
# =========================================================

def get_text(locator, default=""):

    try:

        if locator.count() > 0:

            value = locator.first.inner_text()

            if value:

                return " ".join(
                    value.split()
                )

    except Exception:
        pass

    return default


# =========================================================
# HÀM LẤY ATTRIBUTE
# =========================================================

def get_attribute(
    locator,
    attribute,
    default=""
):

    try:

        if locator.count() > 0:

            value = locator.first.get_attribute(
                attribute
            )

            if value:

                return value.strip()

    except Exception:
        pass

    return default


# =========================================================
# NGỦ NGẪU NHIÊN
# =========================================================

def random_sleep(
    low=DELAY_MIN,
    high=DELAY_MAX
):

    time.sleep(
        random.uniform(
            low,
            high
        )
    )


# =========================================================
# SCROLL
# =========================================================

def scroll_page(page):

    try:

        page.evaluate("""
            window.scrollTo(
                0,
                document.body.scrollHeight
            );
        """)

    except Exception:
        pass


# =========================================================
# KIỂM TRA LINK SẢN PHẨM
# =========================================================

def is_product_url(url):

    if not url:
        return False


    try:

        parsed = urlparse(url)

        path = parsed.path.lower()


    except Exception:

        return False


    # Chỉ lấy link của chính TGDĐ

    if parsed.netloc:

        if parsed.netloc not in [
            "www.thegioididong.com",
            "thegioididong.com"
        ]:

            return False


    # -----------------------------------------------------
    # Các dạng URL sản phẩm
    # -----------------------------------------------------

    product_prefixes = [

        "/dtdd/",

        "/laptop/",

        "/may-tinh-bang/",

        "/dong-ho-thong-minh/",

        "/dong-ho-deo-tay/",

        "/dong-ho/",

        "/phu-kien/",

        "/pc-may-in/"

    ]


    matched = any(
        path.startswith(prefix)
        for prefix in product_prefixes
    )


    if not matched:

        return False


    # -----------------------------------------------------
    # Loại các trang danh mục
    # -----------------------------------------------------

    blocked_paths = [

        "/dtdd",

        "/laptop",

        "/may-tinh-bang",

        "/dong-ho-thong-minh",

        "/dong-ho-deo-tay",

        "/dong-ho",

        "/phu-kien",

        "/pc-may-in"

    ]


    clean_path = path.rstrip("/")


    if clean_path in blocked_paths:

        return False


    return True


# =========================================================
# CHUẨN HÓA URL
# =========================================================

def normalize_url(href):

    if not href:
        return None


    href = href.strip()


    if href.startswith("/"):

        href = urljoin(
            BASE_URL,
            href
        )


    elif href.startswith("http"):

        pass

    else:

        return None


    # Bỏ query
    href = href.split("?")[0]

    # Bỏ fragment
    href = href.split("#")[0]

    # Bỏ dấu /
    href = href.rstrip("/")


    return href


# =========================================================
# LẤY TẤT CẢ LINK SẢN PHẨM TRÊN TRANG
# =========================================================

def collect_links_from_page(
    page,
    category
):

    links = set()


    try:

        anchors = page.locator(
            "a[href]"
        ).all()


        for anchor in anchors:

            try:

                href = anchor.get_attribute(
                    "href"
                )


                href = normalize_url(
                    href
                )


                if not href:
                    continue


                if is_product_url(
                    href
                ):

                    links.add(href)


            except Exception:
                continue


    except Exception as e:

        print(
            f"Lỗi lấy link: {e}"
        )


    return links


# =========================================================
# TÌM NÚT XEM THÊM
# =========================================================

def click_load_more(page):

    button_texts = [

        "Xem thêm",

        "Xem thêm sản phẩm",

        "Tải thêm",

        "Xem thêm sản phẩm khác",

        "Xem thêm nữa",

        "Xem tất cả"

    ]


    clicked = False


    for text in button_texts:

        try:

            buttons = page.get_by_text(
                text,
                exact=True
            )


            count = buttons.count()


            for i in range(count):

                button = buttons.nth(i)


                try:

                    if button.is_visible():

                        page.evaluate(
                            "(el) => el.scrollIntoView({block: 'center'})",
                            button
                        )


                        page.wait_for_timeout(
                            500
                        )


                        button.click(
                            timeout=5000
                        )


                        print(
                            f"      -> Đã bấm: {text}"
                        )


                        page.wait_for_timeout(
                            1500
                        )


                        clicked = True

                        return True


                except Exception:
                    continue


        except Exception:
            continue


    return clicked


# =========================================================
# TÌM PHÂN TRANG
# =========================================================

def get_next_page_url(page):

    selectors = [

        "a.next",

        "a.next-page",

        "a[rel='next']",

        ".pagination a.next",

        "a[aria-label*='Next']",

        "a[aria-label*='next']"

    ]


    for selector in selectors:

        try:

            locator = page.locator(
                selector
            )


            if locator.count() > 0:

                for i in range(
                    locator.count()
                ):

                    element = locator.nth(i)


                    if not element.is_visible():
                        continue


                    href = element.get_attribute(
                        "href"
                    )


                    if href:

                        return normalize_url(
                            href
                        )


        except Exception:
            continue


    return None


# =========================================================
# CÀO TOÀN BỘ LINK CỦA MỘT DANH MỤC
# =========================================================

def collect_all_product_links(
    page,
    category,
    category_url
):

    all_links = set()

    visited_pages = set()

    current_url = category_url

    page_number = 1


    print()
    print("=" * 70)

    print(
        f"DANH MỤC: {category}"
    )

    print("=" * 70)


    while current_url:

        current_url = normalize_url(
            current_url
        )


        if current_url in visited_pages:

            break


        visited_pages.add(
            current_url
        )


        print()
        print(
            f"Trang {page_number}: "
            f"{current_url}"
        )


        try:

            page.goto(
                current_url,
                timeout=PAGE_LOAD_TIMEOUT,
                wait_until="domcontentloaded"
            )


            page.wait_for_timeout(
                2000
            )


        except Exception as e:

            print(
                f"Lỗi mở trang: {e}"
            )

            break


        # -------------------------------------------------
        # LẤY LINK BAN ĐẦU
        # -------------------------------------------------

        old_count = len(
            all_links
        )


        new_links = collect_links_from_page(
            page,
            category
        )


        all_links.update(
            new_links
        )


        print(
            f"      Link mới: "
            f"{len(all_links) - old_count}"
        )


        # -------------------------------------------------
        # TỰ ĐỘNG SCROLL + XEM THÊM
        # -------------------------------------------------

        no_change_count = 0


        for attempt in range(50):

            before = len(
                all_links
            )


            scroll_page(
                page
            )


            page.wait_for_timeout(
                1000
            )


            # Bấm Xem thêm
            clicked = click_load_more(
                page
            )


            # Lấy link mới
            new_links = collect_links_from_page(
                page,
                category
            )


            all_links.update(
                new_links
            )


            after = len(
                all_links
            )


            if after > before:

                print(
                    f"      Đã lấy: "
                    f"{after} sản phẩm"
                )

                no_change_count = 0

            else:

                no_change_count += 1


            # Nếu không có thêm nút
            # và không có sản phẩm mới
            if not clicked:

                if no_change_count >= 3:

                    break


        # -------------------------------------------------
        # KIỂM TRA PHÂN TRANG
        # -------------------------------------------------

        next_url = get_next_page_url(
            page
        )


        if next_url:

            if next_url not in visited_pages:

                print(
                    f"      -> Sang trang tiếp theo"
                )

                current_url = next_url

                page_number += 1

                random_sleep(
                    1,
                    2
                )

                continue


        # Không còn trang tiếp theo
        break


    print()
    print(
        f"HOÀN TẤT {category}: "
        f"{len(all_links)} URL"
    )


    return all_links


# =========================================================
# CÀO CHI TIẾT SẢN PHẨM
# =========================================================

def scrape_product(
    page,
    url,
    category
):

    page.goto(
        url,
        timeout=PAGE_LOAD_TIMEOUT,
        wait_until="domcontentloaded"
    )


    page.wait_for_timeout(
        800
    )


    # -----------------------------------------------------
    # TÊN
    # -----------------------------------------------------

    name = get_text(
        page.locator("h1"),
        "Không có tên"
    )


    # -----------------------------------------------------
    # GIÁ
    # -----------------------------------------------------

    price = ""


    price_selectors = [

        ".box-price-present",

        ".price",

        "[class*='price-present']",

        "[class*='price']"

    ]


    for selector in price_selectors:

        value = get_text(
            page.locator(selector)
        )


        if value and re.search(
            r"\d",
            value
        ):

            price = value

            break


    # -----------------------------------------------------
    # GIÁ CŨ
    # -----------------------------------------------------

    old_price = ""


    old_selectors = [

        ".box-price-old",

        "del",

        "s",

        "[class*='price-old']"

    ]


    for selector in old_selectors:

        value = get_text(
            page.locator(selector)
        )


        if value and re.search(
            r"\d",
            value
        ):

            old_price = value

            break


    # -----------------------------------------------------
    # GIẢM GIÁ
    # -----------------------------------------------------

    discount = ""


    discount_selectors = [

        ".percent",

        "[class*='discount']",

        "[class*='percent']"

    ]


    for selector in discount_selectors:

        value = get_text(
            page.locator(selector)
        )


        if value:

            discount = value

            break


    # -----------------------------------------------------
    # ĐÁNH GIÁ
    # -----------------------------------------------------

    rating = ""


    rating_selectors = [

        ".rating-total",

        "[class*='rating']"

    ]


    for selector in rating_selectors:

        value = get_text(
            page.locator(selector)
        )


        if value:

            rating = value

            break


    # -----------------------------------------------------
    # SỐ ĐÃ BÁN
    # -----------------------------------------------------

    sold = ""


    body_text = get_text(
        page.locator("body")
    )


    match = re.search(
        r"Đã bán\s*([\d,.]+[kK]?)",
        body_text,
        re.IGNORECASE
    )


    if match:

        sold = match.group(1)


    # -----------------------------------------------------
    # ẢNH
    # -----------------------------------------------------

    image = get_attribute(

        page.locator(
            'meta[property="og:image"]'
        ),

        "content"

    )


    # -----------------------------------------------------
    # KẾT QUẢ
    # -----------------------------------------------------

    return {

        "url": url,

        "name": name,

        "category": category,

        "price": price,

        "old_price": old_price,

        "discount": discount,

        "rating": rating,

        "sold": sold,

        "image": image,

        "error": None

    }


# =========================================================
# CHƯƠNG TRÌNH CHÍNH
# =========================================================

def main():

    create_table()


    print()
    print("=" * 70)
    print("THE GIOI DI DONG - FULL PRODUCT CRAWLER")
    print("=" * 70)

    print(
        f"Database: {DATABASE_NAME}"
    )

    print(
        "Chế độ: CÀO TOÀN BỘ SẢN PHẨM"
    )


    with sync_playwright() as p:

        browser = p.chromium.launch(
            headless=HEADLESS
        )


        context = browser.new_context(

            viewport={
                "width": 1920,
                "height": 1080
            },

            user_agent=(
                "Mozilla/5.0 "
                "(Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 "
                "(KHTML, like Gecko) "
                "Chrome/128.0.0.0 "
                "Safari/537.36"
            )
        )


        page = context.new_page()


        # =================================================
        # GIAI ĐOẠN 1
        # GOM TẤT CẢ URL
        # =================================================

        all_products = set()


        for category, category_url in CATEGORY_URLS.items():

            links = collect_all_product_links(

                page,

                category,

                category_url
            )


            for link in links:

                all_products.add(
                    link
                )


            print()
            print(
                f"Tổng URL duy nhất hiện tại: "
                f"{len(all_products)}"
            )


        # =================================================
        # GIỚI HẠN NẾU CÓ
        # =================================================

        product_links = list(
            all_products
        )


        if MAX_PRODUCTS:

            product_links = product_links[
                :MAX_PRODUCTS
            ]


        print()
        print("=" * 70)

        print(
            f"TỔNG URL SẢN PHẨM: "
            f"{len(product_links)}"
        )

        print("=" * 70)


        # =================================================
        # GIAI ĐOẠN 2
        # CÀO TỪNG SẢN PHẨM
        # =================================================

        success = 0

        failed = 0


        for index, url in enumerate(
            product_links,
            start=1
        ):


            print()
            print(
                f"[{index}/{len(product_links)}]"
            )


            # ------------------------------------------------
            # Xác định category từ URL
            # ------------------------------------------------

            category = "Khác"


            path = urlparse(
                url
            ).path.lower()


            if path.startswith("/dtdd/"):

                category = "Điện thoại"

            elif path.startswith("/laptop/"):

                category = "Laptop"

            elif path.startswith("/may-tinh-bang/"):

                category = "Máy tính bảng"

            elif path.startswith("/dong-ho-thong-minh/"):

                category = "Đồng hồ thông minh"

            elif path.startswith("/dong-ho-deo-tay/"):

                category = "Đồng hồ"

            elif path.startswith("/phu-kien/"):

                category = "Phụ kiện"

            elif path.startswith("/pc-may-in/"):

                category = "PC - Máy in"


            try:

                product = scrape_product(

                    page,

                    url,

                    category

                )


                # =============================================
                # LƯU NGAY
                # =============================================

                save_product(
                    product
                )


                success += 1


                print(
                    f"OK -> "
                    f"{product['name'][:80]}"
                )


            except Exception as e:

                failed += 1


                error_message = str(e)[
                    :500
                ]


                print(
                    f"LỖI -> "
                    f"{error_message}"
                )


                # Vẫn lưu URL bị lỗi
                save_product({

                    "url": url,

                    "name": "Không lấy được",

                    "category": category,

                    "price": "",

                    "old_price": "",

                    "discount": "",

                    "rating": "",

                    "sold": "",

                    "image": "",

                    "error": error_message

                })


            random_sleep()


        browser.close()


    # =================================================
    # KẾT QUẢ
    # =================================================

    print()
    print("=" * 70)
    print("CÀO HOÀN TẤT")
    print("=" * 70)

    print(
        f"URL đã xử lý : "
        f"{len(product_links)}"
    )

    print(
        f"Thành công   : "
        f"{success}"
    )

    print(
        f"Lỗi          : "
        f"{failed}"
    )

    print(
        f"Database     : "
        f"{DATABASE_NAME}"
    )

    print("=" * 70)


# =========================================================
# START
# =========================================================

if __name__ == "__main__":

    main()