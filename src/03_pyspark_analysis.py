from pyspark.sql import SparkSession
from pyspark.sql.functions import col, count, avg, sum, desc

# --------------------------------------------------
# 1. Create Spark Session
# --------------------------------------------------
spark = SparkSession.builder \
    .appName("Food Delivery Analytics") \
    .master("local[*]") \
    .getOrCreate()
print("Spark started successfully!")

# --------------------------------------------------
# 2. Load cleaned dataset
# --------------------------------------------------
file_path = "data/cleaned/food_delivery_cleaned.csv"
df = spark.read.csv(
    file_path,
    header=True,
    inferSchema=True
)

# --------------------------------------------------
# 3. Display dataset
# --------------------------------------------------
print("\nFirst 10 records:")
df.show(10, truncate=False)

# --------------------------------------------------
# 4. Show number of records
# --------------------------------------------------
print("\nTotal records:", df.count())

# --------------------------------------------------
# 5. Show columns
# --------------------------------------------------
print("\nColumns:")
print(df.columns)

# --------------------------------------------------
# 6. Show data types
# --------------------------------------------------
print("\nData types:")
df.printSchema()

# --------------------------------------------------
# 7. Basic statistics
# --------------------------------------------------
print("\nBasic statistics:")
df.describe().show()

# --------------------------------------------------
# 8. Missing values
# --------------------------------------------------
print("\nMissing values:")
for column in df.columns:
    missing = df.filter(col(column).isNull()).count()
    print(f"{column}: {missing}")

# --------------------------------------------------
# 9. Stop Spark
# --------------------------------------------------
spark.stop()
print("\nSpark program completed successfully!")