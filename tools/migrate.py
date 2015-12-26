#!/usr/bin/env python3

import requests
import click
import pymysql
import pymysql.cursors
import logging
import pytz
import json

@click.group()
@click.option('--mysql_host', required=True, help="MySQL server to pull data off")
@click.option('--mysql_port', required=True, default=3306, help="MySQL server port")
@click.option('--mysql_user', required=True, help="MySQL user name used to connect to database")
@click.option('--mysql_pass', required=False, help="MySQL user password used to connect to database")
@click.option('--mysql_db', required=True, help="MySQL database used as import source")
@click.option('--rest_url', required=True, help="REST API endpoint used as destination")
@click.option('--debug/--no-debug', is_flag=True, default=False, help="Enable more verbose output from execution")
@click.pass_context
def cli(ctx, mysql_host, mysql_port, mysql_user, mysql_pass, mysql_db, rest_url, debug):
    if debug:
        logging.basicConfig(level=logging.DEBUG, format='%(asctime)s [%(module)s] [%(levelname)s] %(message)s')
    else:
        logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(module)s] [%(levelname)s] %(message)s')
        logging.getLogger("requests").setLevel(logging.WARNING)
        import requests.packages.urllib3
        requests.packages.urllib3.disable_warnings()

    if not mysql_pass:
        mysql_pass = click.prompt("Password for MySQL connection", hide_input=True)

    logging.info("Opening database connection")
    ctx.obj['mysql_connection'] = pymysql.connect(
        host=mysql_host,
        port=mysql_port,
        user=mysql_user,
        password=mysql_pass,
        db=mysql_db,
        charset='utf8mb4',
        cursorclass=pymysql.cursors.DictCursor)
    ctx.obj['rest_url'] = rest_url

def _send_rest_query(url, datapoints):
    rest_query = {
        "api_id": "mawsdata",
        "api_version": 1,
        "query_type": "maws_insert",
        "maws_insert": datapoints
    }
    logging.debug(json.dumps(rest_query, sort_keys=True, indent=4, separators=(',', ': ')))
    r = requests.put(url, data=json.dumps(rest_query), verify=False)
    logging.info(r.json()["maws_insert"])

@cli.command(short_help='Migrate MAWS data')
@click.option('--mysql_table', required=True, help="MySQL source table name")
@click.option('--site_name', required=True, help="Name of the site from which the data is originating from")
@click.option('--table_offset', required=False, default=0, help="Offset for records read from database")
@click.option('--table_amount', required=False, default=0, help="Amount of records to read from database")
@click.option('--rest_amount', required=False, default=1024, help="Amount of records to send in single REST request")
@click.pass_context
def migrate(ctx, site_name, mysql_table, table_offset, table_amount, rest_amount):
    logging.info("Starting migration")
    with ctx.obj["mysql_connection"].cursor() as cursor:
        # construct limiters for SQL query if specified
        if table_amount != 0 or table_offset != 0:
            limit="LIMIT %i,%i" % (table_offset, table_amount)
        else:
            limit=""

        rest_current_limit = 0
        rest_rows = []
        # execute query to database
        cursor.execute("SELECT * FROM %s %s" % (mysql_table, limit))
        for row in cursor:
            #logging.debug(row)
            rest_rows.append({
                "site": site_name,
                "timestamp": row["pvmklo"].replace(tzinfo=pytz.timezone("Europe/Helsinki")).isoformat(),
                "TA60sAvg": row["data1"],
                "DP60sAvg": row["data2"],
                "RH60sAvg": row["data3"],
                "PA60sAvg": row["data4"],
                "QFF60sAvg": row["data5"],
                "SR60sSum": row["data6"],
                "PR60sSum": row["data7"],
                "WD2minAvg": row["data8"],
                "WS2minAvg": row["data9"]
            })
            rest_current_limit = rest_current_limit + 1
            logging.debug("%i/%i" % (rest_current_limit, rest_amount))
            if rest_current_limit == rest_amount:
                # send package, reset counter
                _send_rest_query(ctx.obj['rest_url'], rest_rows)
                rest_current_limit = 0
                rest_rows = []
        if rest_rows.__len__() > 0:
            # empty the pool
            _send_rest_query(ctx.obj['rest_url'], rest_rows)

### start client as main program
def main():
    # init cli interface and start it
    cli(obj=dict())
    sys.exit(0)

if __name__ == '__main__':
    main()

# eof
