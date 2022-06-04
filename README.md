# auto_meal

#### 介绍
针对诚真餐饮设计的自动订餐脚本

#### 安装教程
下载源码 使用corntab等计划任务工具定期执行即可
python >= 3.8
requirement只有requests 自行安装即可

#### 表单数据对应功能：
token: 用户登录标识

preset_date: 预定时间 格式"yyyy-mm-dd"

meal_times_id: 午餐与晚餐对应1和2

meal_type_id: 侧边栏餐品分类，对应id可从MEAL_TYPE接口内获得

meal_id: 特定餐品id，可从MEAL_DATA接口获得

num: 订餐数量 订餐1，不订0（默认）

record_ids: 提交时餐品id 从CART_LIST获得 使用列表形式将所有餐品id一并提交

#### json文件数据：
default.json

"xxx": "MM"  -> MM对应餐次字母代号：例如 ’默认Y‘ 则M为Y 两个M依次对应午饭和晚饭

meal_id.json -> "M": [meal_type_id, meal_id] 依然M代表餐号 列表内两个参数对应各自的表单数据

餐品售罄时，会随机选择订餐（不包括Y Z)

