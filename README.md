# miniyk2012-flask_tutorial
flask官网教程，我仔细学习并写了很多注释

本地启动方法：pip install flask
export FLASK_APP=flaskr
export FLASK_ENV=development
flask run


测试用例运行方法：pip install pytest coverage
在setup.cfg中指定了测试目录和源代码目录
运行pytest
运行获得用例详情：运行pytest -v
运行用例并获得覆盖率：
1. coverage run -m pytest
2. coverage report
3. [optional] coverage html, 覆盖统计会生成在htmlcov目录下