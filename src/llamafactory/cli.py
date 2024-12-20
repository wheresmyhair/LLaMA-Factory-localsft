if __name__ == '__main__':
    import sys
    from os.path import dirname, abspath
    sys.path.insert(0, dirname(dirname(abspath(__file__))))
    from llamafactory._cli import main
    main()