import os  # noqa: F401
import sys  # noqa: F401
from ui import app  # noqa E402
import ui.routes  # noqa E402

if __name__ == '__main__':
    app.run(host="127.0.0.1", port="9999", debug=True)
