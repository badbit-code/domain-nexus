from datetime import datetime
import asyncio

import aiosqlite
import aiohttp

from async_utils import fetch_details, whois

today=f'{datetime.today().strftime("%Y-%m-%d")}'
# today='2021-02-04'


async def db_ops(db_path, table_name, session):
	async with aiosqlite.connect(db_path) as conn, conn.execute(f'select * from {table_name} where date_added = ?', (today,)) as cur:

		async with conn.execute(f'select count(domain_name) from {table_name} where date_added = ?', (today,)) as cur_:
			count = (await cur_.fetchone())[0]
			idx = 0

		# tasks = [asyncio.create_task(fetch_details(row[0], session)) async for row in cur]
		# for details in asyncio.as_completed(tasks):
			# await details

		columns = ('alexa', 'wiki', 'archive_count', 'brandable')
		async for row in cur:
			for column_name, result in zip(columns, await asyncio.create_task(fetch_details(row[0], session))):
				await conn.execute(f'update {table_name} set {column_name}=(?) where domain_name=(?)',(result,row[0]))
				await conn.commit()

			for column_name_tld, exists, creation_date in await whois(row[0]):
				if exists:
					await conn.execute(f'update {table_name} set {column_name_tld}=(?) where domain_name=(?)',(True, row[0]))

					if column_name_tld == row[0].split('.', 1)[-1].lower():
						await conn.execute(f'update {table_name} set creation_date=(?) where domain_name=(?)',(creation_date, row[0]))

				await conn.commit()
					
			idx += 1
			print(f'Added row for {row[0]}, {idx} / {count} completed.')


async def main():
	db_table_pairs = [('db/__godaddy_db.db', 'godaddy_details'), ('db/__sedo_db.db', 'sedo_details')]
	db_table_pairs = [('db/__godaddy_db.db', 'godaddy_details')]
	async with aiohttp.ClientSession() as session:
		for source in db_table_pairs:
			await db_ops(*source, session)

asyncio.run(main(), debug = True)
