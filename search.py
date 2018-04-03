import logging
import requests
import config as config
from scene import Scene


logger = logging.getLogger(__name__)


class SatSearchError(Exception):
    pass


class Query(object):
    """ Класс для осуществления запроса"""

    def __init__(self, **kwargs):
        """ Инициируем объект класса Query с параметрами """
        self.kwargs = kwargs
        self.results = None

    def found(self):
        """ Small query to determine total number of hits """
        if self.results is None:
            self.query(limit=0)
        return self.results['meta']['found']

    def query(self, **kwargs):
        """ Сделать 1 обращение к API """
        kwargs.update(self.kwargs)
        response = requests.get(config.SAT_API, kwargs)

        logger.debug('Запрашиваемый URL: %s' % response.url)

        # если API не отвечает, возвращаем текст http-ответа
        if response.status_code != 200:
            raise SatSearchError(response.text)

        self.results = response.json()
        logger.debug(self.results['meta'])
        return self.results

    def scenes(self, limit=None):
        """ Query and return up to limit results """
        if limit is None:
            limit = self.found()
        limit = min(limit, self.found())
        page_size = min(limit, 1000)

        scenes = []
        page = 1
        while len(scenes) < limit:
            results = self.query(page=page, limit=page_size)['results']
            scenes += [Scene(**r) for r in results]
            page += 1

        return scenes


class Search(object):
    """ Класс для комбинирования к поиску множество запросов """

    def __init__(self, scene_id=[], **kwargs):
        """ Инициируем объект класс Search с параметрами """
        self.queries = []
        if len(scene_id) == 0:
            self.queries.append(Query(**kwargs))
        else:
            for s in scene_id:
                kwargs.update({'scene_id': s})
                self.queries.append(Query(**kwargs))

    def found(self):
        """ Подсчет количества найденных снимков """
        found = 0
        for query in self.queries:
            found += query.found()
        return found

    def scenes(self):
        """ Получить список всех снимков """
        scenes = []
        for query in self.queries:
            scenes += query.scenes()
        return scenes
