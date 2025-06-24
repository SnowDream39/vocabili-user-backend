from app.db.base import Base



# 使用的模型都要导入进来，这是为了给 Alembic 读

import app.users.models
import app.comments.models