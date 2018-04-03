import os
import json
import argparse
import config as config


class SatUtilsParser(argparse.ArgumentParser):

    def __init__(self, search=True, save=True, download=True, output=True, **kwargs):
        """ Initialize a SatUtilsParser """
        dhf = argparse.ArgumentDefaultsHelpFormatter
        super(SatUtilsParser, self).__init__(formatter_class=dhf, **kwargs)
        if search:
            self.add_search_args()
        if save:
            self.add_save_args()
        if download:
            self.add_download_args()
        if output:
            self.add_output_args()
        h = '0:all, 1:debug, 2:info, 3:warning, 4:error, 5:critical'
        self.add_argument('--verbosity', help=h, default=2, type=int)

    def parse_args(self, *args, **kwargs):
        """ Обрабатывает аргументы """
        args = super(SatUtilsParser, self).parse_args(*args, **kwargs)
        args = vars(args)
        args = {k: v for k, v in args.items() if v is not None}
        if 'date' in args:
            dt = args.pop('date').split(',')
            if len(dt) > 2:
                raise ValueError('Укажите диапазон для даты либо как конкретная дата, либо через запятую укажите дату начала и дату окончания ')
            if len(dt) == 1:
                dt = (dt[0], dt[0])
            args['date_from'] = dt[0]
            args['date_to'] = dt[1]

        if 'clouds' in args:
            cov = args.pop('clouds').split(',')
            if len(cov) != 2:
                raise ValueError('Укажите диапазон облачности двумя числами через запятую (например, 0,20)')
            args['cloud_from'] = int(cov[0])
            args['cloud_to'] = int(cov[1])

        # set global configuration options
        if 'datadir' in args:
            config.DATADIR = args.pop('datadir')
        if 'subdirs' in args:
            config.SUBDIRS = args.pop('subdirs')

        return args

    def add_search_args(self):
        """ Добавляет поисковые аргументы для парсера"""
        group = self.add_argument_group('search parameters')
        group.add_argument('--satellite_name', help='Название спутника')
        group.add_argument('--scene_id', help='ID одного или нескольких снимков', nargs='*', default=None)
        group.add_argument('--intersects', help='GeoJSON Feature (либо файл либо строка)')
        group.add_argument('--contains', help='точки с широтой,долготой')
        group.add_argument('--date', help='Либо конкретная дата либо диапазон через запятую (например, 2017-01-01,2017-02-15')
        group.add_argument('--clouds', help='Диапазон допустимого облачного покров (например, 0,20)')
        group.add_argument('--param', nargs='*', help='Дополнительные параметры в форме: KEY=VALUE', action=self.KeyValuePair)

    def add_save_args(self):
        """ Добавляет аргументы для сохранения снимков"""
        group = self.add_argument_group('saving/loading parameters')
        group.add_argument('--load', help='Загружать результаты поиска из файла (игнорирует другие параметры поиска)')
        group.add_argument('--save', help='Сохранить метаданные снимка в виде GeoJSON', default=None)
        group.add_argument('--append', default=False, action='store_true',
                           help='Добавлять снимки к GeoJSON-файлу (указанным с сохранением)')

    def add_download_args(self):
        """ Добавляет аргументы для загрузки снимков"""
        group = self.add_argument_group('download parameters')
        group.add_argument('--datadir', help='Локальная директория, в которую поместить снимки', default=config.DATADIR)
        group.add_argument('--subdirs', default=config.SUBDIRS,
                           help='Сохранять в подпапки на основе метеданных')
        group.add_argument('--download', help='Скачать файлы', default=None, nargs='*')
        group.add_argument('--source', help='Определить источник (доступные: google, aws_s3 - по умолчанию, usgs - требуется регистрация!', 
                            default='aws_s3')

    def add_output_args(self):
        """ Добавляет аргументы для информации вывода """
        group = self.add_argument_group('search output')
        group.add_argument('--printsearch', help='Вывести поисковые параметры', default=False, action='store_true')
        group.add_argument('--printmd', help='Вывести специальные метаданные для указанных снимков', default=None, nargs='*')
        group.add_argument('--printcal', help='Вывести календарь, показывающий даты', default=False, action='store_true')
        group.add_argument('--review', help='Интерактивный просмотр превью снимков', default=False, action='store_true')

    class KeyValuePair(argparse.Action):
        """ Custom action for getting arbitrary key values from argparse """
        def __call__(self, parser, namespace, values, option_string=None):
            for val in values:
                n, v = val.split('=')
                setattr(namespace, n, v)
