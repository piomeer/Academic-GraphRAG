"""
清空 Neo4j 数据库脚本
执行步骤：
1. 连接数据库
2. 查询当前节点数量
3. 删除所有节点和关系
4. 清理索引与约束
5. 最终确认节点数为 0
"""

from neo4j import GraphDatabase
import os
from dotenv import load_dotenv
import sys

load_dotenv()

URI = os.getenv("NEO4J_URI", "bolt://127.0.0.1:7687")
USERNAME = os.getenv("NEO4J_USERNAME", "neo4j")
PASSWORD = os.getenv("NEO4J_PASSWORD", "12345678")


def run_query(tx, query, params=None):
    result = tx.run(query, params or {})
    return result.data()


def main():
    print("=" * 60)
    print("Neo4j 数据库清空工具")
    print("=" * 60)
    print(f"连接至: {URI}")
    print(f"用户名:  {USERNAME}")
    print()

    driver = GraphDatabase.driver(URI, auth=(USERNAME, PASSWORD))

    try:
        # 测试连接
        with driver.session() as session:
            result = session.execute_read(
                lambda tx: tx.run("RETURN 1 AS test").data()
            )
            print("[OK] 数据库连接成功！")
            print()

        # ========== 步骤2: 查询当前节点数量 ==========
        print("-" * 60)
        print("[步骤 1] 查询当前节点数量...")
        with driver.session() as session:
            result = session.execute_read(
                run_query, "MATCH (n) RETURN count(n) AS node_count"
            )
            node_count = result[0]["node_count"]
            print(f"  >> 当前数据库中节点数量: {node_count}")
            print()

        # ========== 步骤3: 删除所有节点和关系 ==========
        if node_count > 0:
            print("-" * 60)
            print("[步骤 2] 删除所有节点和关系...")
            with driver.session() as session:
                session.execute_write(run_query, "MATCH (n) DETACH DELETE n")
                print("  >> DETACH DELETE 执行完毕！所有节点和关系已删除。")
                print()
        else:
            print("数据库已经是空的，跳过删除步骤。")
            print()

        # ========== 步骤4: 清理索引与约束 ==========
        print("-" * 60)
        print("[步骤 3] 清理索引与约束...")

        # 3a: 显示并删除所有约束
        with driver.session() as session:
            constraints = session.execute_read(
                lambda tx: tx.run("SHOW CONSTRAINTS").data()
            )
        print(f"  当前共有 {len(constraints)} 个约束:")
        for c in constraints:
            name = c.get("name", c.get("constraintName", "N/A"))
            print(f"    - {name}")

        with driver.session() as session:
            for c in constraints:
                name = c.get("name", c.get("constraintName"))
                if name:
                    try:
                        session.execute_write(
                            run_query, f"DROP CONSTRAINT {name} IF EXISTS"
                        )
                        print(f"  [DELETED] 约束 '{name}' 已删除")
                    except Exception as e:
                        print(f"  [ERROR] 删除约束 '{name}' 失败: {e}")

        # 3c: 显示并删除所有索引
        with driver.session() as session:
            indexes = session.execute_read(
                lambda tx: tx.run("SHOW INDEXES").data()
            )
        print(f"  当前共有 {len(indexes)} 个索引:")
        for idx in indexes:
            name = idx.get("name", idx.get("indexName", "N/A"))
            print(f"    - {name} (type: {idx.get('type', 'N/A')})")

        with driver.session() as session:
            for idx in indexes:
                name = idx.get("name", idx.get("indexName"))
                if name:
                    try:
                        session.execute_write(
                            run_query, f"DROP INDEX {name} IF EXISTS"
                        )
                        print(f"  [DELETED] 索引 '{name}' 已删除")
                    except Exception as e:
                        print(f"  [ERROR] 删除索引 '{name}' 失败: {e}")

        # 尝试 APOC schema assert
        print()
        print("  [INFO] 尝试通过 APOC 清理 schema 残留...")
        try:
            with driver.session() as session:
                result = session.execute_write(
                    run_query, "CALL apoc.schema.assert({}, {})"
                )
                print("  [OK] APOC schema assert 执行成功")
                for r in result:
                    print(f"       -> {r}")
        except Exception as e:
            print(f"  [INFO] APOC 不可用或执行失败（属正常情况）: {e}")

        print()

        # ========== 步骤5: 最终确认 ==========
        print("-" * 60)
        print("[步骤 4] 最终确认节点数量...")
        with driver.session() as session:
            result = session.execute_read(
                run_query, "MATCH (n) RETURN count(n) AS node_count"
            )
            final_count = result[0]["node_count"]
            print(f"  >> 最终节点数量: {final_count}")

        if final_count == 0:
            print()
            print("=" * 60)
            print("  [OK] 数据库已彻底清空，环境纯净，可以开始 A/B 测试！")
            print("=" * 60)
        else:
            print()
            print("=" * 60)
            print(f"  [WARN] 数据库仍有 {final_count} 个节点，请手动检查。")
            print("=" * 60)

    except Exception as e:
        print(f"\n[ERROR] 发生异常: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

    finally:
        driver.close()


if __name__ == "__main__":
    main()
