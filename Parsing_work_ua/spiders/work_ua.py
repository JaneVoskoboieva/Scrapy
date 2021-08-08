import scrapy


class WorkUaKharkivSpider(scrapy.Spider):
    name = 'work_ua'
    allowed_domains = ['work.ua']
    start_urls = ['https://www.work.ua/resumes-kharkiv/']

    def parse(self, response):
        """
        This function parses name, position, age and link to personal card,
        and collects into dictionary. After this it calls parse_details function
        for collecting description of each job seeker's work detailed information.
        """

        for item in response.css('div#pjax-resume-list div.card.resume-link'):
            card_details_uri = item.css('h2 > a::attr(href)').get()
            position = item.css('h2 a::text').get()
            name = item.css('div > b::text').get().strip()
            age_raw = item.css('div span:nth-child(4)::text').get()[:2]
            if age_raw.strip().isdigit():
                age = int(age_raw)
            else:
                age_raw = item.css('div span:nth-child(3)::text').get()[:2]
                age = int(age_raw)
            result = {
                'Name': name,
                'Position': position,
                'Age': age,
                'link': card_details_uri,
            }
        yield response.follow(card_details_uri, self.parse_details, meta={
                'result': result})

        for page in response.css('ul.pagination li'):
            if page.css('a::text').get() == 'Наступна':
                yield response.follow(
                    page.css('a::attr(href)').get(),
                    self.parse
                )


    def parse_details(self, response):
        """
        This function parses detailed information from job seeker's personal card
        and add the description to the dictionary 'result'
        """

        title = response.css('div.card > h2::text').get()
        description_raw = ' '.join(response.css('div.card > p::text').getall())
        description = ' '.join(description_raw.split())
        response.meta['result']['description'] = title + ': ' + description

        yield response.meta['result']
