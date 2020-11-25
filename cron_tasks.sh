0 3 * * * cd ~/expired_domains && $(which python3.9) ~/expired_domains/sedo_collector.py > /tmp/sedo_collector.logs 2>&1
10 3 * * * cd ~/expired_domains && $(which python3.9) ~/expired_domains/godaddy_collector.py > /tmp/godaddy_collector.logs 2>&1
40 3 * * * cd ~/expired_domains && $(which python3.9) ~/expired_domains/db_ops.py > /tmp/db_ops.logs 2>&1
0 5 * * * cd ~/expired_domains && $(which python3.9) ~/expired_domains/ftp_upload.py > /tmp/ftp_upload.logs 2>&1