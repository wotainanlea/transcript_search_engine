import React, {Component} from 'react'
import classes from './Search.module.css'
import 'bootstrap/dist/css/bootstrap.css'
import axios from 'axios'

const baseURL = "http://localhost:5000"

class Search extends Component {
    state = {
        method: "general",
        field: "all",
        query: "",
        allResults: [],
        results: [],
        currentPage: 1,
        maxItemsPerPage: 10,
        slop: 0
    }

    setField = (event) => {
        this.setState({
            field: event.target.value
        })
    }

    setMethod = (event) => {
        this.setState({
            method: event.target.value
        })
    }

    setSlop = (event) => {
        this.setState({
            slop: event.target.value
        })
    }

    setQuery = (event) => {
        this.setState({
            query: event.target.value
        })
    }

    submitQuery = async() => {
        await axios.get(`${baseURL}/search?method=${this.state.method}&field=${this.state.field}&slop=${this.state.slop}&query=${this.state.query}`)
            .then(response => {
                this.setState({
                    allResults: response.data.results,
                    results: response.data.results,
                    currentPage: 1,
                    method: "general",
                    slop: 0
                })
            })
    }

    goNext = () => {
        this.setState({
            currentPage: this.state.currentPage + 1
        })
    }

    goBack = () => {
        this.setState({
            currentPage: this.state.currentPage - 1
        })
    }

    filterResults = (event, year) => {
        const list = []
        for (let i = 0; i < this.state.allResults.length; i ++) {
            const result = this.state.allResults[i]
            if (result.date.startsWith(year))
                list.push(result)
        }
        this.setState({
            results: list,
            currentPage: 1
        })
    }

    getHighlightedText(text, highlight) {
        if (highlight === "")
            return <span>{text}</span>
        const words = highlight.toLowerCase().split(/[^A-Za-z]/)
        const regex = new RegExp("\\b(" + words.join('|') + "\)+\\b");
        const parts = text.split(regex);
        return <span> { parts.map((part, i) =>
            <span key={i} style={words.includes(part) ? { fontWeight: 'bold' } : {} }>
                { part }
            </span>)
        } </span>;
    }

    async componentDidMount() {
        await axios.get(`${baseURL}/all`)
            .then(response=> {
                this.setState({
                    allResults: response.data.results,
                    results: response.data.results
                })
            })
    }

    render() {
        // console.log(this.state.results)
        console.log(this.state.method)
        const years = [2020, 2019, 2018, 2017, 2016, 2015, 2014, 2013, 2012, 2011, 2010, 2009, 2008, 2007, 2006]
        return(
            <div className={"container " + classes.search}>
                <div className={"mt-5"}>
                    <span className={classes.ted}>TED </span>
                    <span className={classes.talk}>Talks Search</span>
                </div>
                <br/>
                <select className={"btn btn-secondary dropdown-toggle"} style={{height: '35px'}} onChange={this.setField} defaultValue={"all"}>
                    <option value={'all'}>All</option>
                    <option value={'title'}>Title</option>
                    <option value={'speaker'}>Speaker</option>
                    <option value={'description'}>Description</option>
                    <option value={'transcript'}>Transcript</option>
                </select>
                <input type={"text"} placeholder={"Input your query"} style={{width:'500px', height:'35px'}} onChange={this.setQuery}/>
                <button className='btn btn-primary ml-4' onClick={this.submitQuery} style={{height: '35px'}}>Search</button>
                <div className={'mt-3'}>
                    <input type={"radio"} className="form-check-input" value={"general"} onChange={this.setMethod} checked={this.state.method === "general"}/>
                    <label>General search</label>
                    <input type={"radio"} className="form-check-input ml-4" value={"exact"} onChange={this.setMethod} checked={this.state.method === "exact"}/>
                    <label style={{marginLeft: '42px'}}>Exact search</label>
                    <input type={"radio"} className="form-check-input ml-4" value={"proximity"} onChange={this.setMethod} checked={this.state.method === "proximity"}/>
                    <label style={{marginLeft: '42px'}}>Proximity search</label>
                </div>
                {
                    this.state.method === "proximity" ?
                        <div>
                            <label>Slop</label>
                            <input className={"ml-2"} type={"text"} placeholder={"Max search window"} onChange={this.setSlop}/>
                        </div> : null
                }
                <div className={'mt-3'}>
                    <div className={'row'}>
                        <div className={'col-lg-1 ml-n5'}>
                            {years.map((year, index) =>
                                <button className={classes.link+" btn btn-link"} onClick={(event) => this.filterResults(event, ''+year)}>{year}</button>
                            )}
                        </div>
                        <div className={classes.resultCard} style={{marginLeft: '150px'}}>
                            <p className={classes.resultsCount + " mb-1"}>{this.state.results.length} results found</p>
                            {
                                this.state.results.slice((
                                    this.state.currentPage*this.state.maxItemsPerPage)-this.state.maxItemsPerPage,
                                    this.state.currentPage*this.state.maxItemsPerPage)
                                    .map((result, index) =>
                                    <div>
                                        <div className={"mb-n2"}>
                                            <small>{result.url}</small>
                                        </div>
                                        <a className={classes.title} href={result.url}>{result.title}</a>
                                        <p className={classes.description+" mt-1"}>{this.getHighlightedText(result.description, this.state.query)}</p>
                                        <div className={classes.talkInfo + " mb-3 mt-n3"}>
                                            <span>Speaker: {result.speaker}</span>
                                            <span className={"ml-5"}>Date: {result.date}</span>
                                            <span className={"ml-5"}>Duration: {Math.floor(result.duration/60)} mins</span>
                                            <span className={"ml-5"}>Views: {result.views}</span>
                                        </div>
                                    </div>
                                )
                            }
                            <div className={classes.search+" mb-5"}>
                                {this.state.currentPage > 1 ?
                                    <button className={'btn btn-light mr-2'} onClick={this.goBack}>back</button> : null}
                                {this.state.results.length > 0 ?
                                    <span>- {this.state.currentPage} -</span> : null}
                                {this.state.results.length -1 > this.state.currentPage * this.state.maxItemsPerPage ?
                                    <button className={'btn btn-light ml-2'} onClick={this.goNext}>next</button> : null}
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        )
    }
}

export default Search