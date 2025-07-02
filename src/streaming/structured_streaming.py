from pyspark.sql import SparkSession
from pyspark.sql.functions import from_json, col, explode
from pyspark.sql.types import StructType, ArrayType, StringType, DoubleType, BooleanType, StructField
from src.db.db_connections import connect_db_sqlalchemy




spark = SparkSession.builder \
    .appName("FlightDataStream") \
    .config("spark.jars", "/app/jars/postgresql-42.6.0.jar") \
    .getOrCreate()

# Leitura do Kafka (raw)
df_raw = spark.readStream \
    .format("kafka") \
    .option("kafka.bootstrap.servers", "localhost:9092") \
    .option("subscribe", "flight-data-raw") \
    .load()

df_json = df_raw.selectExpr("CAST(value AS STRING)")

# Define schema para o array de estados
state_schema = ArrayType(StructType([
    StructField("icao24", StringType()),
    StructField("callsign", StringType()),
    StructField("origin_country", StringType()),
    StructField("time_position", DoubleType()),
    StructField("last_contact", DoubleType()),
    StructField("longitude", DoubleType()),
    StructField("latitude", DoubleType()),
    StructField("baro_altitude", DoubleType()),
    StructField("on_ground", BooleanType()),
    StructField("velocity", DoubleType()),
    StructField("heading", DoubleType()),
    StructField("vertical_rate", DoubleType()),
    StructField("sensors", StringType()),
    StructField("geo_altitude", DoubleType()),
    StructField("squawk", StringType()),
    StructField("spi", BooleanType()),
    StructField("position_source", StringType())
]))

# Função para transformação — recebe DataFrame raw e retorna DataFrame transformado
def transform_data_spark(df):
    # Decodifica o JSON, explode o array "states" e cria colunas limpas
    df_parsed = df.withColumn(
        "json_data", 
        from_json(col("value"), StructType().add("states", state_schema))
    ).select(explode(col("json_data.states")).alias("state"))

    df_clean = df_parsed.select(
        col("state.icao24").alias("icao24"),
        col("state.callsign").alias("callsign"),
        col("state.origin_country").alias("origin_country"),
        col("state.time_position").cast("timestamp").alias("time_position"),
        col("state.last_contact").cast("timestamp").alias("last_contact"),
        col("state.longitude").alias("longitude"),
        col("state.latitude").alias("latitude"),
        col("state.baro_altitude").alias("baro_altitude"),
        col("state.on_ground").alias("on_ground"),
        col("state.velocity").alias("velocity"),
        col("state.heading").alias("heading"),
        col("state.geo_altitude").alias("geo_altitude")
    )
    return df_clean

df_transformed = transform_data_spark(df_json)

def upsert_to_postgres(df, epoch_id):
    if df.rdd.isEmpty():
        return

    engine = connect_db_sqlalchemy()
    jdbc_url = str(engine.url)
    connection_properties = {
        "user": engine.url.username,
        "password": engine.url.password,
        "driver": "org.postgresql.Driver"
    }

    staging_table = "flight_data_staging"
    target_table = "flight_data"

    # 1. Grava batch no staging
    df.write \
      .jdbc(url=jdbc_url, table=staging_table, mode='overwrite', properties=connection_properties)

    # 2. Merge no banco
    merge_sql = f"""
    INSERT INTO {target_table} (
        icao24, callsign, origin_country, time_position,
        last_contact, longitude, latitude, baro_altitude,
        on_ground, velocity, heading, geo_altitude
    )
    SELECT
        icao24, callsign, origin_country, time_position,
        last_contact, longitude, latitude, baro_altitude,
        on_ground, velocity, heading, geo_altitude
    FROM {staging_table}
    ON CONFLICT (icao24, time_position)
    DO UPDATE SET
        last_contact = EXCLUDED.last_contact,
        velocity = EXCLUDED.velocity,
        heading = EXCLUDED.heading;
    """

    with engine.connect() as conn:
        conn.execute(merge_sql)

df_transformed.writeStream \
    .foreachBatch(upsert_to_postgres) \
    .outputMode("update") \
    .start() \
    .awaitTermination()
