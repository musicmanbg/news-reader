from pydantic import BaseModel


class HtmlSource(BaseModel):
    url: str
    html_content: str
    encoding: str
