import imghdr
import os
import shutil
from multiprocessing import Pool

import requests

from links import Links


class GoogleImageCrawler:
    def __init__(self, skip=True, n_threads=4, path=""):
        self.skip = skip
        self.n_threads = n_threads
        self.path = path
    
    def report(self):
        pass
    
    def crawl(self):
        keywords = self.keywords()
        tasks = []

        for keyword in keywords:
            dir_name = '{}/{}'.format(self.path, keyword)
            if os.path.exists(os.path.join(os.getcwd(), dir_name)) and self.skip:
                print('Skipping directory already existing{}.'.format(dir_name))
                continue

        tasks.append(keyword)
  
        pool = Pool(self.n_threads)
        pool.map_async(self.download, tasks)
        pool.close()
        pool.join()
        print('Task ended. Pool join.')

        self.report()

        print('End Program')
    
    @staticmethod
    def get_extension(link, default='jpg'):
        splits = str(link).split('.')
        if len(splits) == 0:
            return default
        ext = splits[-1].lower()
        if ext == 'jpg' or ext == 'jpeg':
            return 'jpg'
        elif ext == 'gif':
            return 'gif'
        elif ext == 'png':
            return 'png'
        else:
            return default

    @staticmethod
    def save(response, path):
        pass

    @staticmethod
    def validate(path):
        ext = imghdr.what(path)
        if ext == 'jpeg':
            ext = 'jpg'
        return ext

    def download(self, keyword):
        source = Links()
        print('Collecting downloadable links of {}...'.format(keyword))
        links = source.collect(keyword)

        print('Downloading images of {} from collected links...'.format(keyword))
        self.mkdir('{}/{}'.format(self.path, keyword))
        n_links = len(links)
        for index, link in enumerate(links):
            try:
                print('Downloading this image based on the keyword {} from {}: {}/{}'.format(keyword, link, index + 1, n_links))
                response = requests.get(link, stream=True)
                ext = self.get_extension(link)
                raw_path = '{}/{}/{}'.format(self.path, keyword, str(index).zfill(4))
                path = raw_path + '.' + ext
                self.save(response, path) 

                del response

                print("Validating image file")
                ext2 = self.validate(path)
                if ext2 is None:
                    print('Unreadable file - {}'.format(link))
                    os.remove(path)
                else:
                    if ext != ext2:
                        path2 = raw_path + '.' + ext2
                        os.rename(path, path2)
                        print('Renaming extension {} -> {}'.format(ext, ext2))
            except Exception as e:
                print('Download failed.', e)
                continue

    @staticmethod
    def mkdir(name):
        current_path = os.getcwd()
        path = os.path.join(current_path, name)
        if not os.path.exists(path):
            os.makedirs(path)

    @staticmethod
    def keywords(file='keywords.txt'):
        with open(file, 'r', encoding='utf-8-sig') as f:
            text = f.read()
            lines = text.split('\n')
            lines = filter(lambda x: x != '' and x is not None, lines)
            keywords = sorted(set(lines))

        return keywords

if __name__ == '__main__':
    crawler = GoogleImageCrawler()
    crawler.crawl()