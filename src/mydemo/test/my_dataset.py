import asyncio

from crawlee.storages import Dataset, KeyValueStore


async def main() -> None:
    # Open dataset manually using asynchronous constructor open().
    dataset = await Dataset.open()

    # Interact with dataset directly.
    await dataset.push_data({'a': 'b'})

    kvs = await KeyValueStore.open()
    await kvs.set_value(
        key=f'screenshot-test',
        value=screenshot,
        content_type='image/png',
    )

if __name__ == '__main__':
    asyncio.run(main())