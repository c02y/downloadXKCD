#! python3

import requests, os, bs4, sys

import argparse

# import pil
# from PIL import Image

dir = "xkcd"

def checkImageOK(file):
    "TODO, wrong: Check if an image is broken"
    try:
        im = Image.open(file)
        im.verify()
    except IOError as e:
        return False


def checkFileExisted(file):
    "Check if the file already existed and not empty"
    return False
# TODO:
    if os.path.exists(file) and checkImageOK(file):
        return True
    else:
        return False


def downloadPage(url):
    "Download a page and return the result"
    # Download the page
    print("Downloading page %s..." % url)
    res = requests.get(url)
    res.raise_for_status()
    return res


def saveImage(res, dir, imageNum, comicUrl):
    "Save Image to disk"
    imagePath = os.path.join(dir, str(imageNum) + "-" + os.path.basename(comicUrl))
    if checkFileExisted(imagePath):
        print("Image %s already existed..." % imagePath)
        return
    else:
        imageFile = open(imagePath, 'wb')
        for chunk in res.iter_content(100000):
            imageFile.write(chunk)

            imageFile.close()
            print("Saving image to: " + imagePath)


def downloadImage(soup, dir, comicUrl):
    "Download ComicUrl page"
    # Download the image
    print('Downloading image %s...' % (comicUrl))
    res = requests.get(comicUrl)
    res.raise_for_status()
    prevLink = soup.select('a[rel="prev"]')[0]
    imageNum = getImageNum(soup, prevLink)
    saveImage(res, dir, imageNum, comicUrl)

    return prevLink


def getImageNum(soup, prevLink):
    "get the image number"
    if prevLink.get('href') == "#":
        imageNum = 1
    else:
        imageNum = int(prevLink.get('href')[1:-1]) + 1

    return imageNum


def findComicUrl(soup, res):
    "Find comic url"
    comicElem = soup.select('#comic img')
    if comicElem == []:
        print('Could not find comic image.')
        return
    else:
        comicUrl = "http:" + comicElem[0].get('src')

    return comicUrl

def downloadAll(url='https://xkcd.com/'):
    "Download all comic images from XKCD, by default from the latest to 1"
    while not url.endswith('#'):    # previous page of page1 endswith '#'
        res = downloadPage(url)

        soup = bs4.BeautifulSoup(res.text, "lxml")

        comicUrl = findComicUrl(soup, res)

        if comicUrl:
            prevLink = downloadImage(soup, dir, comicUrl)
            url = 'http://xkcd.com' + prevLink.get('href')


def downloadAll2(url='https://xkcd.com/'):
    """
    One in all function:
    Download all comic images from XKCD, by default from the latest to 1
    """
    # url = 'https://xkcd.com/'
    while not url.endswith('#'):    # previous page of page1 endswith '#'
        # Download the page
        print("Downloading page %s..." % url)
        res = requests.get(url)
        res.raise_for_status()

        soup = bs4.BeautifulSoup(res.text, "lxml")

        # Find the url of the comics image
        comicElem = soup.select('#comic img')
        if comicElem == []:
            print('Could not find comic image.')
        else:
            comicUrl = "http:" + comicElem[0].get('src')
            # Download the image
            print('Downloading image %s...' % (comicUrl))
            res = requests.get(comicUrl)
            res.raise_for_status()

            # get the current image number
            prevLink = soup.select('a[rel="prev"]')[0]
            # previous page of page1 is '#'
            if prevLink.get('href') == "#":
                imageNum = 1
            else:
                imageNum = int(prevLink.get('href')[1:-1]) + 1

            # Save the image to ./xkcd by default
            imagePath = os.path.join(dir, str(imageNum) + "-" + os.path.basename(comicUrl))

            # Check if the same file already downloaded
            if checkFileExisted(imagePath):
                print("Image %s already existed..." % imagePath)
            else:
                imageFile = open(imagePath, 'wb')
                for chunk in res.iter_content(100000):
                    imageFile.write(chunk)

                    imageFile.close()
                    print("Saving image to: " + imagePath)

            url = 'http://xkcd.com' + prevLink.get('href')


def downloadOne(url='http://xkcd.com'):
    "Download one specific xkcd image, by default, the latest one"
    if not url.endswith('#'):
        res = downloadPage(url)

        soup = bs4.BeautifulSoup(res.text, "lxml")

        comicUrl = findComicUrl(soup, res)

        downloadImage(soup, dir, comicUrl)


def downloadOne2(url='http://xkcd.com'):
    """
    One in all function:
    Download specific comic image from XKCD, by default the latest
    """
    if not url.endswith('#'):
        print("Download single page %s..." % url)
        res = requests.get(url)
        res.raise_for_status()

        soup = bs4.BeautifulSoup(res.text, "lxml")

        # Find the url of the comics image
        comicElem = soup.select('#comic img')
        if comicElem == []:
            print("Could not find comic image.")
        else:
            comicUrl = "http:" + comicElem[0].get('src')
            # Download the image
            print('Downloading single image %s...' % (comicUrl))
            res = requests.get(comicUrl)
            res.raise_for_status()

            # get the current image number
            prevLink = soup.select('a[rel="prev]"')[0]
            # previous page of page1 is '#'
            if prevLink.get('href') == "#":
                imageNum = 1
            else:
                imageNum = int(prevLink.get('href')[1:-1]) + 1

            # Save the image to ./
            imagePath = os.path.join(dir, str(imageNum) + "-" + os.path.basename(comicUrl))
            # Check if the same file already downloaded
            if checkFileExisted(imagePath):
                print("Image %s already existed..." % imagePath)
            else:
                imageFile = open(imagePath, 'wb')
                for chunk in res.iter_content(100000):
                    imageFile.write(chunk)

                    imageFile.close()
                    print("Saving image to: " + imagePath)


def main():
    descStr = """
    This program download comic images from https://xkcd.com.
    """
    parser = argparse.ArgumentParser(description=descStr)

    parser.add_argument('-d', dest="dir", required=False,
                        help="the directory you want to store the downloaded images")

    group = parser.add_mutually_exclusive_group()

    group.add_argument('-a', nargs="?", required=False,
                       help="download all comic images, from latest/NUM to the first one")
    group.add_argument('-s', nargs="+", dest="NUMs", required=False,
                       help="download the comic image of page http://xkcd.com/NUM[1,2,...]")

    args = parser.parse_args()

    if args.dir is not None:
        # print("dir is " + args.d)
        global dir
        dir = args.dir

    os.makedirs(dir, exist_ok=True)

    # Note the following block and order of if-else
    if (args.dir is None and len(sys.argv) <= 1) or (args.dir is not None and len(sys.argv) == 3):
        print("No argv, download the latest comic image")
        downloadOne()
    elif args.a is not None:
        if args.a != '':
            print("-a NUM, download all comics images older than http://xkcd.com/" + args.a)
            downloadAll('http://xkcd.com/' + args.a)
    elif args.NUMs is not None:
        for i in args.NUMs:
            print("-s [NUM1, NUM2...] argv, downloading comic image from page http://xkcd.com/" + i)
            downloadOne("http://xkcd.com/" + i)
    else:
        print("-a, download all comic images")
        downloadAll()

if __name__ == '__main__':
    main()
