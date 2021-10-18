import scrapy

class AO3Spider(scrapy.Spider):
    name = "ao3"
    min_page = 1
    max_page = 999999

    def start_requests(self):
        relationships = [
            "Sherlock Holmes/John Watson",
            "Draco Malfoy/Harry Potter",
            "Steve Rogers/Tony Stark",
            "Castiel/Dean Winchester"
        ]
        for page in range(int(self.min_page), int(self.max_page)):
            for relationship in relationships:
                yield scrapy.Request(
                    "https://archiveofourown.org/tags/" + relationship.replace("/", "*s*") + "/works?page=" + str(page),
                    callback=self.parse_relationship,
                    cb_kwargs={"relationship": relationship})

    def parse_relationship(self, response, relationship):
        '''Find authors on each relationship page'''
        page_authors = response.xpath("//a[@rel='author']/@href").getall()
        page_authors = [p.split("/")[-1] for p in page_authors]

        for username in page_authors:
            if username != "orphan_account":
                yield scrapy.Request(
                        'https://archiveofourown.org/users/'+ username + '/works',
                        callback=self.parse_author,
                        cb_kwargs={"relationship": relationship})


    def parse_author(self, response, relationship):
        '''Find works on each author page'''
        page_works = response.xpath("//h4[@class='heading']/a/@href").getall()
        page_works = [w.split("/")[-1] for w in page_works if w.startswith("/works/")]
        for work_id in page_works:
            yield scrapy.Request(
                'https://archiveofourown.org/works/'+ work_id + '?view_adult=true&amp;view_full_work=true',
                callback=self.parse_story,
                cb_kwargs={"relationship": relationship, "work_id": work_id})

    def parse_story(self, response, relationship, work_id):
        '''Extract story data'''
        def unpack_if_single(l):
            if len(l) == 1:
                return l[0]
            return l

        #*********
        # Get IP
        # def get_ip(self, response):
        #     self.log('IP : %s' % response.css('#ip_address').get())
        #     print('IP : %s' % response.css('#ip_address').get())
        # scrapy.Request("http://ifconfig.me", callback=get_ip)



        #*******

        summary_ps = response.xpath("//div[@class='summary module']//blockquote//text()").getall()
        summary_ps = [p.strip() for p in summary_ps]
        summary = "\n".join(summary_ps).strip()

        text_ps = response.xpath("//div[@id='chapters']//p/text()").getall()
        text_ps = [p.strip() for p in text_ps]
        text = "\n".join(text_ps).strip()

        metadata =  {
            "author": response.xpath("//a[@rel='author']//text()").get().strip(),
            "summary": summary,
            "full_text": text,
            "url": response.url,
            "work_id": work_id,
            "title": response.xpath("//h2[@class='title heading']//text()").get().strip(),
            "fandoms": unpack_if_single(response.xpath("///dd[@class='fandom tags']//a//text()").getall()),
            "category": unpack_if_single(response.xpath("///dd[@class='category tags']//a//text()").getall()),
            "relationship": unpack_if_single(response.xpath("///dd[@class='relationship tags']//a//text()").getall()),
            "rating": unpack_if_single(response.xpath("///dd[@class='rating tags']//a//text()").getall()),
            "warning": unpack_if_single(response.xpath("///dd[@class='warning tags']//a//text()").getall()),
            "characters": unpack_if_single(response.xpath("///dd[@class='character tags']//a//text()").getall()),
            "language": response.xpath("///dd[@class='language']//text()").get().strip(),
        }
        if isinstance(metadata["relationship"], str) and metadata["relationship"] == relationship and metadata["language"] == "English":
            yield metadata
