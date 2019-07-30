from django.urls import reverse
from django.contrib import admin

from patent.custom_site import custom_site
from .adminforms import PostAdminForm
from .models import Post, Category, Tag
from django.utils.html import format_html


@admin.register(Tag, site=custom_site)
class TagAdmin(admin.ModelAdmin):
    list_display = ("name", "status", "created_time")
    fields = ("name", "status")

    def save_model(self, request, obj, form, change):
        obj.owner = request.user
        return super(TagAdmin, self).save_model(request, obj, form, change)


class CategoryOwnerFilter(admin.SimpleListFilter):
    """自定义过滤器, 只展示当前用户分类"""
    title = "分类过滤器"
    parameter_name = "owner_category"

    def lookups(self, request, model_admin):
        return Category.objects.filter(owner=request.user).values_list("id", "name")

    def queryset(self, request, queryset):
        category_id = self.value()
        if category_id:
            return queryset.filter(category_id=self.value())
        return queryset


@admin.register(Post, site=custom_site)
class PostAdmin(admin.ModelAdmin):
    form = PostAdminForm
    list_display = ["title", "category", "status", "created_time", "owner", "operator"]
    list_display_links = []  # 配置哪些字段可以作为链接, 点击他们进入编辑页面
    list_filter = [CategoryOwnerFilter]  # 配置页面过滤器, 需要通过哪些字段来过滤列表
    search_fields = ["title", "category_name"]  # 配置搜索字段
    actions_on_top = True  # 动作相关配置, 是否展示在顶部
    actions_on_bottom = True  # 动作相关配置, 是否展示在底部
    exclude = ('owner',)

    # 编辑页面
    save_on_top = True  # 保存, 编辑, 编辑并新建的 按钮 是否在顶部展示
    # fields = (
    #     ("category", "title"),
    #     "desc",
    #     "status",
    #     "content",
    #     "tag",
    # )
    fieldsets = (  # 用来控制布局 ==> (当前模块的名称, {内容:当前模块的描述, 字段和样式配置}),
        (
            "基础配置", {
                "description": "基础配置描述",
                "fields": (
                    ('title', 'category'),
                    'status',
                ),
            }
        ), (
            "内容", {
                'fields': (
                    'desc', 'content'
                ),
            }
        ), (
            "额外信息", {
                'classes': ('collapse',),
                'fields': ('tags',),
            }
        )
    )

    def operator(self, obj):  # 自定义函数的参数是一定的就是当前 行 的对象, 列表中的每一行对应数据库表中的一条数据, 也对应Model中的一个实例
        # return format_html("<a href='{}'>编辑</a>", reverse("admin:blog_post_change", args=(obj.id,)))
        return format_html("<a href='{}'>编辑</a>", reverse("cus_admin:blog_post_change", args=(obj.id,)))

    operator.short_description = "操作"

    def save_model(self, request, obj, form, change):
        obj.owner = request.user
        return super(PostAdmin, self).save_model(request, obj, form, change)

    def get_queryset(self, request):
        qs = super(PostAdmin, self).get_queryset(request)
        return qs.filter(owner=request.user)

    # 自定义导入静态资源 ==> 可以通过Media() 类来向页面中添加想要的Javascript和CSS资源
    class Media():
        css = {
            "all": ("https://cdn.bootcss.com/bootstrap/4.0.0-beta.2/css/bootstrap.min.css"),
        }
        js = ("https://cdn.bootcss.com/bootstrap/4.0.0-beta.2/bootstrap.bundle.js")


# 在页面中编辑关联数据
class PostInline(admin.TabularInline):  # StackedInline  样式不同
    fields = ('title', 'desc')
    extra = 1  # 控制额外多几个
    model = Post


@admin.register(Category, site=custom_site)
class CategoryAdmin(admin.ModelAdmin):
    inlines = [PostInline, ]
    list_display = ("name", "status", "is_nav", "created_time", "post_count")  # 这里显示的是修改数据之后后台可以看到的页面中的数据
    fields = ("name", "status", "is_nav")  # 这是用户添加数据的时候可以看到的页面

    def save_model(self, request, obj, form, change):
        obj.owner = request.user  # 把当前登录的用户赋值给obj.owner ==> 如果未登录通过request.user拿到匿名用户对象
        return super(CategoryAdmin, self).save_model(request, obj, form, change)  # change用来保存当前数据是新增的还是更新的

    def post_count(self, obj):
        return obj.post_set.count()

    post_count.short_description = "文章数量"
