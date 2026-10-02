import sqlite3

# =========================================================
# DATABASE
# =========================================================

DATABASE_NAME = "thegioididong.db"

def connect_db():
    return sqlite3.connect(
        DATABASE_NAME
    )

# =========================================================
# XEM TOÀN BỘ SẢN PHẨM
# =========================================================

def show_all_products():

    print()
    print("=" * 120)
    print("DANH SÁCH SẢN PHẨM")
    print("=" * 120)

    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            id,
            name,
            category,
            price,
            old_price,
            rating,
            sold
        FROM Product
        ORDER BY id
    """)

    products = cursor.fetchall()
    conn.close()

    if not products:
        print("Database chưa có sản phẩm.")
        return

    print(
        f"{'ID':<5}"
        f"{'TÊN SẢN PHẨM':<50}"
        f"{'LOẠI':<20}"
        f"{'GIÁ':<18}"
        f"{'ĐÁNH GIÁ':<10}"
        f"{'ĐÃ BÁN':<10}"
    )

    print("-" * 120)

    for product in products:

        product_id = product[0]

        name = product[1] or ""

        category = product[2] or ""

        price = product[3] or ""

        rating = product[5] or ""

        sold = product[6] or ""

        name = name[:47]

        category = category[:17]

        print(
            f"{product_id:<5}"
            f"{name:<50}"
            f"{category:<20}"
            f"{price:<18}"
            f"{rating:<10}"
            f"{sold:<10}"
        )

    print("-" * 120)

    print(
        f"Tổng số: {len(products)} sản phẩm"
    )

# =========================================================
# TÌM SẢN PHẨM
# =========================================================

def find_product():
    print()
    print("=" * 60)
    print("TÌM SẢN PHẨM")
    print("=" * 60)

    keyword = input(
        "Nhập tên sản phẩm cần tìm: "
    ).strip()

    if not keyword:
        print(
            "Từ khóa không được để trống."
        )
        return

    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            id,
            name,
            category,
            price,
            old_price,
            discount,
            rating,
            sold,
            url
        FROM Product
        WHERE name LIKE ?
        ORDER BY id
    """, (
        "%" + keyword + "%",
    ))

    products = cursor.fetchall()
    conn.close()

    if not products:
        print(
            "Không tìm thấy sản phẩm."
        )
        return

    for product in products:
        print()
        print("-" * 80)

        print(
            "ID       :",
            product[0]
        )

        print(
            "Tên      :",
            product[1]
        )

        print(
            "Loại     :",
            product[2]
        )

        print(
            "Giá      :",
            product[3]
        )

        print(
            "Giá cũ   :",
            product[4]
        )

        print(
            "Giảm giá :",
            product[5]
        )

        print(
            "Đánh giá :",
            product[6]
        )

        print(
            "Đã bán   :",
            product[7]
        )

        print(
            "URL      :",
            product[8]
        )

        print("-" * 80)

# =========================================================
# XEM CHI TIẾT
# =========================================================

def view_product():

    print()
    print("=" * 60)
    print("XEM CHI TIẾT SẢN PHẨM")
    print("=" * 60)

    try:
        product_id = int(
            input("Nhập ID sản phẩm: ")
        )

    except ValueError:
        print(
            "ID không hợp lệ."
        )
        return

    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            id,
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
        FROM Product
        WHERE id = ?
    """, (
        product_id,
    ))

    product = cursor.fetchone()
    conn.close()

    if product is None:
        print(
            "Không tìm thấy sản phẩm."
        )
        return

    print()

    print("ID       :", product[0])
    print("URL      :", product[1])
    print("Tên      :", product[2])
    print("Loại     :", product[3])
    print("Giá      :", product[4])
    print("Giá cũ   :", product[5])
    print("Giảm giá :", product[6])
    print("Đánh giá :", product[7])
    print("Đã bán   :", product[8])
    print("Hình ảnh :", product[9])

    if product[10]:
        print()
        print("LỖI:")
        print(product[10])

# =========================================================
# THÊM SẢN PHẨM THỦ CÔNG
# =========================================================

def add_product():

    print()
    print("=" * 60)
    print("THÊM SẢN PHẨM")
    print("=" * 60)

    url = input(
        "URL: "
    ).strip()

    name = input(
        "Tên sản phẩm: "
    ).strip()

    category = input(
        "Loại sản phẩm: "
    ).strip()

    price = input(
        "Giá: "
    ).strip()

    old_price = input(
        "Giá cũ: "
    ).strip()

    discount = input(
        "Giảm giá: "
    ).strip()

    rating = input(
        "Đánh giá: "
    ).strip()

    sold = input(
        "Đã bán: "
    ).strip()

    image = input(
        "Link hình ảnh: "
    ).strip()

    if not url or not name:
        print(
            "URL và tên không được để trống."
        )
        return

    conn = connect_db()
    cursor = conn.cursor()

    try:
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
        """, (
            url,
            name,
            category,
            price,
            old_price,
            discount,
            rating,
            sold,
            image,
            None
        ))

        conn.commit()
        print(
            "Thêm sản phẩm thành công!"
        )

    except sqlite3.IntegrityError:
        print(
            "URL sản phẩm đã tồn tại!"
        )

    finally:
        conn.close()

# =========================================================
# XÓA SẢN PHẨM
# =========================================================

def delete_product():

    print()
    print("=" * 60)
    print("XÓA SẢN PHẨM")
    print("=" * 60)

    try:
        product_id = int(
            input("Nhập ID sản phẩm: ")
        )
    except ValueError:
        print(
            "ID không hợp lệ."
        )
        return

    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, name
        FROM Product
        WHERE id = ?
    """, (
        product_id,
    ))

    product = cursor.fetchone()

    if product is None:
        print(
            "Không tìm thấy sản phẩm."
        )
        conn.close()
        return

    print()
    print(
        "Sản phẩm:",
        product[1]
    )


    confirm = input(
        "Bạn có chắc chắn muốn xóa? (y/n): "
    )

    if confirm.lower() != "y":
        print(
            "Đã hủy."
        )
        conn.close()
        return

    cursor.execute(
        "DELETE FROM Product WHERE id = ?",
        (product_id,)
    )

    conn.commit()
    conn.close()

    print(
        "Xóa sản phẩm thành công!"
    )

# =========================================================
# XÓA TOÀN BỘ
# =========================================================

def delete_all_products():
    print()
    print("=" * 60)
    print("XÓA TOÀN BỘ SẢN PHẨM")
    print("=" * 60)

    confirm = input(
        "Bạn có chắc muốn xóa TẤT CẢ? (y/n): "
    )

    if confirm.lower() != "y":
        print(
            "Đã hủy."
        )
        return

    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute(
        "DELETE FROM Product"
    )

    conn.commit()
    conn.close()

    print(
        "Đã xóa toàn bộ sản phẩm!"
    )

# =========================================================
# MENU
# =========================================================

def show_menu():

    print()
    print("=" * 60)
    print("       THE GIOI DI DONG - PRODUCT MANAGEMENT")
    print("=" * 60)

    print("1. Xem toàn bộ sản phẩm")
    print("2. Tìm sản phẩm")
    print("3. Xem chi tiết sản phẩm")
    print("4. Thêm sản phẩm")
    print("5. Xóa sản phẩm")
    print("6. Xóa toàn bộ sản phẩm")
    print("0. Thoát")

    print("=" * 60)

# =========================================================
# MAIN
# =========================================================

def main():
    while True:
        show_menu()

        choice = input(
            "Nhập lựa chọn: "
        ).strip()

        if choice == "1":
            show_all_products()

        elif choice == "2":
            find_product()

        elif choice == "3":
            view_product()

        elif choice == "4":
            add_product()

        elif choice == "5":
            delete_product()

        elif choice == "6":
            delete_all_products()

        elif choice == "0":
            print(
                "Goodbye!"
            )
            break

        else:
            print(
                "Lựa chọn không hợp lệ!"
            )

# =========================================================
# START
# =========================================================

if __name__ == "__main__":
    main()