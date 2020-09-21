import pymssql #引入pymssql模块
from DBUtils.PooledDB import PooledDB

if __name__ == '__main__':
    #conn = conn()
    pool = PooledDB(pymssql,
        mincached=5, maxcached=10, maxshared=5, maxconnections=10, blocking=True,
                 maxusage=100, setsession=None, reset=True,
                 host='10.4.23.101',
                 user='GZ_MES', password='mes@_123'
         )

    
    conn = pool.connection()
    cursor = conn.cursor()
    cursor.execute("""select * from dbo.v_ASRS_STORE_MESVIEW""")
    if cursor.description is not None:
        columns = [row[0] for row in cursor.description]
        print(columns)
        print("*"*100)
        data =  cursor.fetchall()
        print(type(data))
        for x in data:
            print(x)
        # print(data)