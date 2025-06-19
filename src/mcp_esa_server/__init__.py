from . import server


def main():
    """このパッケージのメインエントリポイント"""
    server.main()


# パッケージレベルで公開する他のアイテム
__all__ = ["main", "server"]
