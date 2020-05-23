# docker-flask
create flask env by invenio

create new module:
cookiecutter https://github.com/inveniosoftware/cookiecutter-invenio-module.git -o moudles/

invenio db init
invenio alembic revision "Create wepy model branch." -b wxpy_index -p dbdbc1b19cf2 --empty
pip install -e /code/modules/wxpy-index
invenio db create -v
invenio alembic upgrade heads
invenio alembic revision "add unionid for wepy_user."
invenio alembic upgrade

# 环境部署
docker-compose build
docker-compose up -d
docker-compose exec wepy_server ./entrypoint.sh
docker-compose restart wepy_server
docker-compose exec wepy_server invenio db init
# 参照7行