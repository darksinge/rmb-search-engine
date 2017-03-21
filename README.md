## IR Utah Legislation Project

Craig Blackburn, Whitney DeSpain, Bradley Robinson

## 1    Introduction

While politics is important to many people, getting involved and understandinglegislature can be a hard task for the average person.  We seek to make it lessdifficult by giving Utahans a new way to look at bills going through our statelegislature.  Our goal is to develop a software tool that automates the processof presenting relevant and engaging legislative data.

Since the development of the [website][ratemybill] used to display our findings is concern of it's own, [it's source code is hosted in a seperate repository][ratemybill-github].

## 2    Utah Legislation Classification Tool

### 2.1 Tool Function

Our tool will make it easier for Utahan’s to sort through the large volume ofbills that are presented each year by classifying bills of similarity.It will also provide social-media features such as commenting, user responses,and an up/down-voting system.  This will help Utah citizens learn, understand,and become more involved with bills presented to the Utah legislature while si-multaneously providing additional data to improve classification and determinerelevance of bills.

### 2.2 User Audience and Benefits of Tool

Utah legislation is confusing and can be difficult to understand.  Hundreds ofbills are presented to the Utah State legislature every year.  Our tool would helppeople  become  more  involved  as  citizens  by  providing  accessible  informationin an concise intuitive way.  The current search tool available onle.utah.govis confusing and difficult to navigate, especially for someone who is unfamiliarwith the functions of state legislation.

### 2.3 Project Challenges and Differences of Existing Tools

The challenge of this project will be developing the underlying algorithms thatwill allow our website to classify and present useful and relevant information to end users.

While the state of Utah publishes information online about each bill that is discussed in both the House and Senate, they are organized in an unintuitive way that makes it difficult for civic-minded Utahan’s to get a big picture of what is going on in state government.  Discussions about these bills can happen other places such as Facebook, Twitter, and news site comment boards.  However, a website dedicated to the discussion of these bills that presents information that's easy to understand would be unique.

### 2.4    Project Development & Algorithms
 
We will use data obtained from government websites (le.utah.gov) that host current  and  past  legislative  bills.   One  of  our  main  goals  will  be  to  create  a clustering algorithm that will allow us to see which bills are more closely related to each other and then group them accordingly on the website. 

We’ll  also  gather  data  on  voting  behavior  of  representatives  in  our  state government to perform analytics that accurately predict if a given piece of legislation will pass or fail. 

To help accomplish these design goals, we will use algorithms such as,
 * K-Means to classify the bills into clusters.
 * Search using tf-idf sorting.
 * Vector Space Classification (e.g., Rocchio, kNN) to determine similarityof bills.
 
Implementation of a website will provide an interface to present data to usersin a meaningful format.  We can gather data from comments, a voting system, user  behavior,  and  user  feedback  with  the  addition  of  a  social  media  feature to improve the accuracy and relevance of our clustering and search algorithm results.
 
### 2.5    Resources

Possible resources we can use in our project

* data collection: TheBeautifulSoup4andScrapy Pythonlibraries to crawland organize publicly available data on the legislative website.
* data storage: A MySQL database to store and access data.
* text processing: NLTK and SKLearn to  process  text  data  and  create  K-Means.
* presentation: A  visualization  library  (Matplotlib  or  D3)  to  help  users see interesting relationships about legislators in Utah and voting over the years.
* search queries: Existing  algorithms  to  build  an  inverted  index,  tokenize terms, and support advanced searches (and, or, not, inclusive, exclusive, permuterm, parametric queries, etc.)
* web interface: NodeJS runtime environment to build a website that displays our findings and research.

[ratemybill]: https://ratemybill.com
[ratemybill-github]: https://github.com/darksinge/ratemybill-site
