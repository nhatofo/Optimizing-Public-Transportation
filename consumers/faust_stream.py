"""Defines trends calculations for stations"""
import logging
import faust

logger = logging.getLogger(__name__)

class Station(faust.Record):
    stop_id: int
    direction_id: str
    stop_name: str
    station_name: str
    station_descriptive_name: str
    station_id: int
    order: int
    red: bool
    blue: bool
    green: bool

class TransformedStation(faust.Record):
    station_id: int
    station_name: str
    order: int
    line: str

app = faust.App("stations-stream", broker="kafka://localhost:9092", store="memory://")
topic = app.topic("com.udacity.stations", value_type=Station)
out_topic = app.topic("com.udacity.staions.table", partitions=1)
table = app.Table(
    "com.udacity.stations.table.v1",
    default=TransformedStation,
    partitions=1,
    changelog_topic=out_topic,
)

@app.agent(topic)
async def process(info_stream):
    async for info in info_stream:
        line = None

        if info.red is True:
            line = 'red'
        elif info.blue is True:
            line = 'blue'
        elif info.green is True:
            line = 'green'
        else:
            logger.info(f"No line color for {info.station_id}")

        transformed = TransformedStation(
            station_id=info.station_id,
            station_name=info.station_name,
            order=info.order,
            line=line
        )
        table[info.station_id] = transformed

if __name__ == "__main__":
    app.main()
