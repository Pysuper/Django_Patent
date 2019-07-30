from django.contrib.admin import AdminSite


class CustomSite(AdminSite):
    """
    定制site:
        把 `用户管理模块` 和 ` 文章分类数据的管理` 分开
        修改后台的默认展示 (Django站点管理后台) ==> SmallSpider
    """
    site_header = 'SmallSpider'
    site_title = 'SmallSpider管理后台'
    index_title = '首页'


custom_site = CustomSite(name='cus_admin')
