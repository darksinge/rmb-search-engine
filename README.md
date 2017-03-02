# Utah Legislature IR Project

## Project Proposal

1-2 page proposal - brief descriptive title of your project.
 
#### What is exactly the function of your tool? That is, what will it do? 
 
 Have another resource to access Utah's legislative bills with social-media (emoticons for user response) type features to help users learn more about bills. It will also make it easier for Utahns to sort through the large volume of bills that are passed each year by grouping them by similarity.

#### Why would we need such a tool and who would you expect to use it and benefit from it? 
 
 Utah politics can seem inaccessible and there are a lot of bills that get passed, this would help people who want to be involved to access information in a more intuitive way.

#### Does this kind of tools already exist? If similar tools exist, how is your tool different from them? Would people care about the   difference? How hard is it to build such a tool? What is the challenge?

... While Utah does publish online information about each bill that is discussed in both the House and Senate, they are organized in an unintuitive way that makes it difficult for civic-minded Utahns to get a big picture of what is going on in Utah politics.  

#### How do you plan to build it? You should mention the data you will use and the core algorithm that you will implement.

We will use data obtained from government websites (le.utah.gov) that host current and past legislative bills. One of our main goals will be to create a clustering algorithm that will allow us to see which bills are more closely related to each other and then group them accordingly on the website. We'll also gather data on the different representatives in our state government to perform analytics to accurately predict if a given piece of legislation will pass or fail.

Our core algorithms will be:

1. K-means to classify the bills into clusters
2. Search using tf-idf sorting

Another feature we hope to implement is an online interface that will present data to users in a meaningful format that is clear and easy to understand via a web interface. After adding this social media aspect of the project, we can gather data from comments, a voting system, user behavior, and user feedback to improve the accuracy and relevance of our clustering and search algorithm results.

#### What existing resources can you use?

* The BeautifulSoup4 and Scrapy Python libraries to crawl and organize the data that is publicly available on the legislative web site.
* A database such as SQL to store and access the data.
* NLTK and SKLearn to process text data and create K-Means.
* A visualization library (Matplotlib or D3) to help users see interesting relationships about legislators in Utah and voting over the years.
* Existing algorithms to build an inverted index, tokenize terms, and support advanced searches (and, or, not, inclusive, exclusive, permuterm, parametric queries, etc.)
* Web frameworks (NodeJS) to build a website that can display our findings and research


#### How will you demonstrate the usefulness of your tool?
...

