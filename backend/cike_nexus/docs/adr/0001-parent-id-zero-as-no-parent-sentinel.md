# 用 `parent_id = 0` 表示「无上级」，而非 `NULL` 或真实的根部门记录

部门需要表达上下级关系，「顶级部门」的「无上级」状态有三种建模方式。我们选择哨兵值 `0`：`parent_id = 0` 读作「我没有上级」，表里**不存在** `id = 0` 的记录，因此部门树可以有多个顶级部门。

## 为什么不是真实的根部门记录

直觉上最干净的做法是在表里放一条 `id = 0` 的「集团」记录，让整棵树单根收口。**这条记录在 MySQL 上建不出来。** `department.id` 是 `AUTO_INCREMENT` 主键，而 MySQL 对自增列的行为是：

> Normally, you generate the next sequence number for the column by inserting either `NULL` or `0` into it. `NO_AUTO_VALUE_ON_ZERO` suppresses this behavior for `0` so that only `NULL` generates the next sequence number.
> —— [MySQL 8.4 Reference Manual, Server SQL Modes](https://dev.mysql.com/doc/refman/8.4/en/sql-mode.html)

`INSERT ... id = 0` 会被当成「帮我分配下一个」，实际落库是 `id = 1`。要真的存进 `0`，必须启用 `NO_AUTO_VALUE_ON_ZERO`——那是实例级/会话级开关，影响该库中**所有表的所有插入**，且换部署环境漏配就会静默失效。为一行种子数据换一个全局数据库开关，不划算。

## 为什么不是 `NULL`

`NULL` 在语义上更标准，但 `parent_id` 已经以 `NOT NULL DEFAULT 0` 落进初始迁移。改成可空需要一次迁移加存量数据订正，换来的只是口味上的纯粹，没有行为收益。同时 `NULL` 在 SQL 里不参与等值比较，「查同级部门」这类查询要写成 `parent_id IS NULL OR parent_id = ?` 的分支，反而更啰嗦。

## 后果

- **部门树是森林，不是单根树。** 树接口返回的是顶级部门的数组，不是单个对象。
- **`parent_id = 0` 跳过父节点校验。** 其他取值必须校验目标部门存在且未被软删除。
- **`0` 永远不是一个合法的部门 id。** 任何以 `0` 作为部门 id 传入的请求都是非法参数。
- 如果将来需要「唯一顶级部门」的形态（例如公司本体作为唯一根节点），加一条「至多允许一个 `parent_id = 0` 的部门」的业务校验即可，**不需要迁移**，本决定不构成阻碍。
