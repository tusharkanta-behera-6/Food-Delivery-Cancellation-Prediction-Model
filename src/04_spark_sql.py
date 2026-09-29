from pyspark.sql import SparkSession

print("Initializing Spark Session...")

# Create Spark Session (Local Mode)
spark = SparkSession.builder \
    .appName("FoodDeliverySparkSQL") \
    .master("local[*]") \
    .config("spark.sql.shuffle.partitions", "4") \
    .getOrCreate()

# Reduce logging noise
spark.sparkContext.setLogLevel("ERROR")
print("Spark SQL started successfully!\n")

# Load the cleaned dataset
file_path = "data/cleaned/food_delivery_cleaned.csv"
print(f"Loading data from: {file_path}")
df = spark.read.csv(file_path, header=True, inferSchema=True)

# Register as a temporary SQL table
df.createOrReplaceTempView("orders")
print(f"Dataset loaded successfully! Total Orders: {df.count()}\n")

print("="*60)
print("1. ORDERS BY PERIOD")
print("="*60)
spark.sql("""
    SELECT Order_Period, COUNT(*) as Total_Orders
    FROM orders
    WHERE Order_Period IS NOT NULL
    GROUP BY Order_Period
    ORDER BY Total_Orders DESC
""").show()

print("="*60)
print("2. ORDERS BY DAY")
print("="*60)
spark.sql("""
    SELECT Day, COUNT(*) as Total_Orders
    FROM orders
    WHERE Day IS NOT NULL
    GROUP BY Day
    ORDER BY Total_Orders DESC
""").show()

print("="*60)
print("3. TOP 5 RESTAURANTS")
print("="*60)
spark.sql("""
    SELECT `Restaurant name`, COUNT(*) as Total_Orders
    FROM orders
    WHERE `Restaurant name` IS NOT NULL AND `Restaurant name` NOT LIKE '%off%'
    GROUP BY `Restaurant name`
    ORDER BY Total_Orders DESC
    LIMIT 5
""").show(truncate=False)

print("="*60)
print("4. AVERAGE ORDER VALUE (Safely ignoring bad data)")
print("="*60)
spark.sql("""
    SELECT 
        ROUND(AVG(CAST(Total AS DOUBLE)), 2) AS Average_Order_Value,
        ROUND(MIN(CAST(Total AS DOUBLE)), 2) AS Min_Order_Value,
        ROUND(MAX(CAST(Total AS DOUBLE)), 2) AS Max_Order_Value
    FROM orders
    WHERE Total RLIKE '^[0-9]+(\\.[0-9]+)?$'
""").show()

print("="*60)
print("5. AVERAGE PREP & WAIT TIMES")
print("="*60)
spark.sql("""
    SELECT 
        ROUND(AVG(CAST(`KPT duration (minutes)` AS DOUBLE)), 2) AS Avg_Prep_Time_Min,
        ROUND(AVG(CAST(`Rider wait time (minutes)` AS DOUBLE)), 2) AS Avg_Rider_Wait_Min
    FROM orders
    WHERE `KPT duration (minutes)` RLIKE '^[0-9]+(\\.[0-9]+)?$'
""").show()

print("="*60)
print("6. ORDER STATUS / CANCELLATION OVERVIEW")
print("="*60)
spark.sql("""
    SELECT `Order Status`, COUNT(*) as Count
    FROM orders
    WHERE `Order Status` IS NOT NULL
    GROUP BY `Order Status`
    ORDER BY Count DESC
""").show()

print("="*60)
print("✅ Spark SQL Analysis Completed Successfully!")
print("="*60)

# Stop the Spark session
spark.stop()