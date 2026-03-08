import webbrowser
import sys

def test_webbrowser():
    url = "https://www.google.com"
    print(f"Testing webbrowser.open('{url}')...")
    success = webbrowser.open(url)
    if success:
        print("webbrowser.open returned True (Success indication)")
    else:
        print("webbrowser.open returned False (Failure indication)")

if __name__ == "__main__":
    test_webbrowser()
