import datetime
import fabric.functions as fn
import logging

udf = fn.UserDataFunctions()

# ==============================================================================
# PHASE 7.3 - PRODUCT REPOSITORY
# ==============================================================================


# ==============================================================================
# 7.3.1 - FETCH PRODUCT BY GOLD PRODUCT ID
# ==============================================================================

def fetch_product_by_id(cursor, productId: str):
    """
    Fetch consolidated product details from gold.products.

    Returns:
        dict: Product details if found.
        None: If product does not exist.
    """

    query = """
        SELECT
            GoldProductId,
            ProductName,
            Description,
            CAST(Price AS FLOAT) AS Price,
            Brand,
            Category,
            Color,
            Size,
            Material,
            InStock,
            SourceRecordCount
        FROM gold.products
        WHERE GoldProductId = ?
    """

    cursor.execute(query, (productId,))

    row = cursor.fetchone()

    if row is None:
        return None

    return {
        "goldProductId": row[0],
        "productName": row[1],
        "description": row[2],
        "price": row[3],
        "brand": row[4],
        "category": row[5],
        "color": row[6],
        "size": row[7],
        "material": row[8],
        "inStock": bool(row[9]) if row[9] is not None else None,
        "sourceRecordCount": int(row[10]) if row[10] is not None else None
    }


# ==============================================================================
# 7.3.2 - FETCH PRODUCT FIELD-LEVEL LINEAGE
# ==============================================================================

def fetch_product_lineage(cursor, productId: str):
    """
    Fetch field-level lineage from gold.productlineage.

    Returns:
        list: Lineage records for the requested product.
    """

    query = """
        SELECT
            GoldProductId,
            FieldName,
            SelectedValue,
            SourceSystem,
            SourceRecordId,
            SourceUpdatedAt,
            SurvivorshipRule
        FROM gold.productlineage
        WHERE GoldProductId = ?
        ORDER BY FieldName
    """

    cursor.execute(query, (productId,))

    rows = cursor.fetchall()

    lineage_records = []

    for row in rows:

        lineage_records.append({
            "goldProductId": row[0],
            "fieldName": row[1],
            "selectedValue": row[2],
            "sourceSystem": row[3],
            "sourceRecordId": row[4],
            "sourceUpdatedAt": row[5],
            "survivorshipRule": row[6]
        })

    return lineage_records


# ==============================================================================
# PHASE 7.5 - PRODUCT DETAILS API
# ==============================================================================

@udf.connection(argName="lakehouse", alias="ProductCatalogL")
@udf.function()
def get_product_details(
    productId: str,
    lakehouse: fn.FabricLakehouseClient
) -> dict:
    """
    Retrieve complete consolidated product details
    along with field-level lineage.
    """

    # --------------------------------------------------------------------------
    # Step 1: Validate input
    # --------------------------------------------------------------------------

    if not productId or not productId.strip():

        return {
            "success": False,
            "errorCode": "INVALID_PRODUCT_ID",
            "message": "Product ID cannot be empty."
        }

    productId = productId.strip()

    connection = None
    cursor = None

    try:

        # ----------------------------------------------------------------------
        # Step 2: Establish Lakehouse SQL connection
        # ----------------------------------------------------------------------

        connection = lakehouse.connectToSql()
        cursor = connection.cursor()

        # ----------------------------------------------------------------------
        # Step 3: Retrieve consolidated product
        # ----------------------------------------------------------------------

        product = fetch_product_by_id(
            cursor,
            productId
        )

        # ----------------------------------------------------------------------
        # Step 4: Handle nonexistent product
        # ----------------------------------------------------------------------

        if product is None:

            return {
                "success": False,
                "errorCode": "PRODUCT_NOT_FOUND",
                "message": "Product not found.",
                "productId": productId
            }

        # ----------------------------------------------------------------------
        # Step 5: Retrieve field-level lineage
        # ----------------------------------------------------------------------

        lineage = fetch_product_lineage(
            cursor,
            productId
        )

        # ----------------------------------------------------------------------
        # Step 6: Build API response
        # ----------------------------------------------------------------------

        return {
            "success": True,
            "product": product,
            "lineageCount": len(lineage),
            "lineage": lineage
        }

    except Exception as e:

        logging.exception(
            "Product details API execution failed."
        )

        return {
            "success": False,
            "errorCode": "PRODUCT_DETAILS_ERROR",
            "message": "Unable to retrieve product details.",
            "error": str(e)
        }

    finally:

        # ----------------------------------------------------------------------
        # Step 7: Release resources
        # ----------------------------------------------------------------------

        if cursor is not None:
            cursor.close()

        if connection is not None:
            connection.close()

# ==============================================================================
# PHASE 7.4 - PRODUCT SEARCH
# 7.4.1 - SEARCH PRODUCTS BY NAME WITH PAGINATION
# ==============================================================================


def fetch_product_search_results(
    cursor,
    searchTerm: str,
    pageNumber: int,
    pageSize: int
):
    """
    Search consolidated products by product name.

    Supports:
        - Partial matching
        - Case-insensitive matching
        - Relevance-based ordering
        - Pagination
        - Total matching record count
    """

    searchPattern = f"%{searchTerm}%"
    prefixPattern = f"{searchTerm}%"

    # --------------------------------------------------------------------------
    # Step 1: Get total matching product count
    # --------------------------------------------------------------------------

    countQuery = """
        SELECT COUNT_BIG(*)
        FROM gold.products
        WHERE LOWER(ProductName) LIKE LOWER(?)
    """

    cursor.execute(countQuery, (searchPattern,))

    totalCount = int(cursor.fetchone()[0])

    # --------------------------------------------------------------------------
    # Step 2: Calculate pagination offset
    # --------------------------------------------------------------------------

    offset = (pageNumber - 1) * pageSize

    # --------------------------------------------------------------------------
    # Step 3: Retrieve paginated search results
    # --------------------------------------------------------------------------

    searchQuery = """
        SELECT
            GoldProductId,
            ProductName,
            Description,
            CAST(Price AS FLOAT) AS Price,
            Brand,
            Category,
            Color,
            Size,
            Material,
            InStock,
            SourceRecordCount
        FROM gold.products
        WHERE LOWER(ProductName) LIKE LOWER(?)

        ORDER BY
            CASE
                WHEN LOWER(ProductName) = LOWER(?) THEN 1
                WHEN LOWER(ProductName) LIKE LOWER(?) THEN 2
                ELSE 3
            END,
            ProductName,
            GoldProductId

        OFFSET ? ROWS
        FETCH NEXT ? ROWS ONLY
    """

    cursor.execute(
        searchQuery,
        (
            searchPattern,
            searchTerm,
            prefixPattern,
            offset,
            pageSize
        )
    )

    rows = cursor.fetchall()

    products = []

    # --------------------------------------------------------------------------
    # Step 4: Convert SQL records into dictionaries
    # --------------------------------------------------------------------------

    for row in rows:

        products.append({
            "goldProductId": row[0],
            "productName": row[1],
            "description": row[2],
            "price": row[3],
            "brand": row[4],
            "category": row[5],
            "color": row[6],
            "size": row[7],
            "material": row[8],
            "inStock": bool(row[9]) if row[9] is not None else None,
            "sourceRecordCount": int(row[10]) if row[10] is not None else None
        })

    totalPages = (
        (totalCount + pageSize - 1) // pageSize
        if totalCount > 0 else 0
    )

    return {
        "searchTerm": searchTerm,
        "totalCount": totalCount,
        "pageNumber": pageNumber,
        "pageSize": pageSize,
        "totalPages": totalPages,
        "hasNextPage": pageNumber < totalPages,
        "hasPreviousPage": pageNumber > 1,
        "products": products
    }


# ==============================================================================
# 7.4.1 - PUBLIC PRODUCT SEARCH FUNCTION
# ==============================================================================

@udf.connection(argName="lakehouse", alias="ProductCatalogL")
@udf.function()
def search_products(
    searchTerm: str,
    pageNumber: int,
    pageSize: int,
    lakehouse: fn.FabricLakehouseClient
) -> dict:

    # --------------------------------------------------------------------------
    # Step 1: Validate inputs
    # --------------------------------------------------------------------------

    if not searchTerm or not searchTerm.strip():

        return {
            "success": False,
            "message": "Search term cannot be empty."
        }

    searchTerm = searchTerm.strip()

    if pageNumber < 1:

        return {
            "success": False,
            "message": "Page number must be greater than zero."
        }

    if pageSize < 1 or pageSize > 100:

        return {
            "success": False,
            "message": "Page size must be between 1 and 100."
        }

    connection = None
    cursor = None

    try:

        # ----------------------------------------------------------------------
        # Step 2: Establish Lakehouse SQL connection
        # ----------------------------------------------------------------------

        connection = lakehouse.connectToSql()

        cursor = connection.cursor()

        # ----------------------------------------------------------------------
        # Step 3: Execute product search
        # ----------------------------------------------------------------------

        results = fetch_product_search_results(
            cursor,
            searchTerm,
            pageNumber,
            pageSize
        )

        # ----------------------------------------------------------------------
        # Step 4: Return search response
        # ----------------------------------------------------------------------

        return {
            "success": True,
            **results
        }

    except Exception as e:

        logging.exception("Product search operation failed.")

        return {
            "success": False,
            "message": "Unable to search products.",
            "error": str(e)
        }

    finally:

        # ----------------------------------------------------------------------
        # Step 5: Release resources
        # ----------------------------------------------------------------------

        if cursor is not None:
            cursor.close()

        if connection is not None:
            connection.close()