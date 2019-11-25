from airflow import DAG
from airflow.operators.bash_operator import BashOperator
from datetime import datetime, timedelta


default_args = {
  "owner": "ikedaosushi",
  'depends_on_past' : True,
  "start_date": datetime(2019, 1, 10),
}

dag = DAG("test", default_args=default_args, schedule_interval=None)

t1 = BashOperator(
  task_id="touch_file",
  bash_command="touch test.txt",
  dag=dag
)

cmd = r'curl -X POST --data-urlencode "payload={\"channel\": \"#debug\", \"username\": \"webhookbot\", \"text\": \"hello from airflow\", \"icon_emoji\": \":ghost:\"}" https://hooks.slack.com/services/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'
t2 = BashOperator(
  task_id="slack_post",
  bash_command=cmd,
  dag=dag
)