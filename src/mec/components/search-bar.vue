<template>

     <div class="row">
         
         <loading :active="isLoading"
                 :can-cancel="true"  
                 :is-full-page="fullPage"/>
                 
        <div class="col-md-3">
            <div class="card">

                
               
                <div class="card-body">

                    <div class="row">   
                        <div class="col-md-12">

                          
                            <h4>Serie de tiempo</h4>

                            <div class="form-group">
                                <label for="">Métrica</label>
                                <select @change="onChangeMetric($event)"  v-model="form.metric" class="form-control ">
                                    <option :value="metric" v-for="(metric, i) in metrics" :key="i">{{metric.fields.metric}}</option>
                                </select>
                            </div>

                            <div class="form-group">
                                <label for="">Componente</label>
                                <select  v-model="form.component" class="form-control ">
                                    <option :value="component" v-for="(component, i) in components" :key="i">{{component.component}}</option>
                                </select>
                            </div>

    
                            <div v-show='filters.length'>
                                <h4 class='mt-4'>Filtros</h4>

                                <div class="form-group " style="position:relative"  v-for="(filter, i) in filters" :key="i">
                                    <label for="">{{filter.name | pretty }}</label>
                                    <!-- {{stepFilter}} - {{i}}
                                 :disabled='stepFilter < i'  -->

                                  
                                    <select @change='changeFilter'  v-model="form.filters[filter.key]" class="form-control ">
                                        <option value=""></option>
                                        <option :value="data" v-for="(data, i) in filter.data" :key="i">{{data[1]}}</option>
                                    </select>
                        
                                    <!-- <strong v-if='form.filters[filter.key]' @click='clearFilter(filter.key)' style="cursor:pointer; position:absolute; right: 22px; top: 35px;"><i class="fas fa-times"></i></strong> -->
                                </div>

                            </div>
                           <h4 class='mt-4'>Invervalos</h4>

                             <div class="row">
                                <div class="col-md-6">
                                    <div class="form-group">
                                        <label for="">Fecha inicial:</label> <br>
                                        <date-picker v-model="form.start_date"></date-picker>
                                        <!-- <input v-model="form.start_date" type="text" class="form-control" placeholder="Fecha de entrada en operacion">  -->
                                    </div>
                                </div>
                                <div class="col-md-6">
                                     <div class="form-group">
                                        <label for="">Fecha final:</label>
                                        <date-picker v-model="form.limit_date" ></date-picker>
                                        <!-- <input v-model="form.limit_date" type="text" class="form-control" placeholder="Fecha limite de operacion">  -->
                                    </div>
                                </div>
                            </div>


                            <div class="form-group">
                                <label for="">Periodicidad deseada</label>
                                <select  v-model="form.period" class="form-control ">
                                    <option :value="period" v-for="(period, i) in periods" :key="i">{{period[1]}}</option>
                                </select>
                            </div>

                           


                            <div class="form-group">
                                <label for="">Método de resampleo</label>
                                <select  v-model="form.resample" class="form-control ">
                                    <option :value="resample" v-for="(resample, i) in resamples" :key="i">{{resample[1]}}</option>
                                </select>
                            </div>

                            <div class="form-group">
                                <label for="">Eje</label>
                                <select  v-model="form.axis" class="form-control ">
                                    <option value="y">Primero</option>
                                    <option value="y2">Segundo</option>
                                    <option value="y3">Tercero</option>
                                    <option value="y4">Cuarto</option>
                                </select>
                            </div>                            


                            <button :disabled="!form.component" @click="addSerie" class='btn btn-success btn-block'>Agregar Serie</button>
                            
                            
                        </div>
                    </div>
                    
                </div>
            </div>
        </div>
        <div class="col-md-9">
            
            <div class="card" >      
                <div class="card-body">

                                 
                    <div v-show='forms.length'>
                    
                        <h4>Características de las series</h4>
                        <table class="table table-bordered">
                            <thead>
                                <tr>
                                    <th></th>
                                    <th>Eje</th>
                                    <th>Componente</th>
                                    <th>Periodicidad</th>
                                    <th>Metodo de resampleo</th>
                                    <th>Unidades</th>
                                    <th>Fecha</th>
                                    <th>Filtros</th>
                                    <th></th>
                                </tr>
                            </thead>
                            <tbody>
                                <tr v-for="(form, i) in forms" :key="i" v-bind:class="{ 'table-success': i == formSelected }">
                                    <td>
                                        <input @click="setFormSelected(i)" name='radio' type="radio" :checked='i == formSelected'>
                                    </td>
                                    <td>{{form.axis}}</td>
                                    <td>{{form.component.component}}</td>
                                    <td>{{form.period[1]}}</td>
                                    <td>{{form.resample[1]}}</td>
                                    <td>{{form.unit}}</td>
                                    <td>{{form.start_date | moment}} - {{form.limit_date | moment}}</td>
                                    <td>
                                        <div>
                                            <small   v-for="(item, i) in form.f" :key="i">
                                                
                                                <span v-if='item'><strong>{{i|pretty}}:</strong> {{item[1]}}<br></span>
                                            </small>
                                        </div>
                                    </td>
                                    <td>
                                        <button @click="deleteSerie(i)" class='btn btn-danger btn-sm'>
                                            <i class="fas fa-trash"></i>
                                        </button>
                                    </td>
                                </tr>
                            </tbody>
                        </table>

                    </div>

                    <div id="serieChart"></div>

                    <div v-show='forms.length'>
                        <h4 class='mt-5'>Estadísticas descriptivas</h4>

                        <table class='table table-bordered'>
                            <thead>
                                <tr>
                                    <th>Componente</th>
                                    <th>Media</th>
                                    <th>Mediana</th>
                                    <th>Maxima</th>
                                    <th>Minima</th>
                                    <th>Percentil 05</th>
                                    <th>Percentil 95</th>
                                    <th>Desviación estandar</th>
                                </tr>
                            </thead>
                            <tbody>
                                <tr v-for="(form, i) in forms" :key="i">
                                    <td>{{form.component.component}}</td>
                                    <td>{{form.response.average | toFixed}}</td>
                                    <td>{{form.response.median | toFixed}}</td>
                                    <td>{{form.response.maximum | toFixed}}</td>
                                    <td>{{form.response.minimum | toFixed}}</td>
                                    <td>{{form.response.percentile_05 | toFixed}}</td>
                                    <td>{{form.response.percentile_95 | toFixed}}</td>
                                    <td>{{form.response.standard_deviation | toFixed}}</td>
                                </tr>
                            </tbody>
                        </table>

                    
                        
                    </div>


                    <div id="histogramChart"></div>

    
                    <button v-show='this.forms.length' @click="exportData" class='btn btn-success btn-block'>Exportar resultados</button>

                </div>
            </div>
        </div>
     </div>
    
</template>

<script>
    import DatePicker from 'vue2-datepicker';
    import Loading from 'vue-loading-overlay';
    import vSelect from 'vue-select'
    import 'vue-loading-overlay/dist/vue-loading.css';
    import 'vue2-datepicker/index.css';
    import 'vue-select/dist/vue-select.css';
    import moment from 'moment';


    export default {
        props: ['metrics', 'components_url', 'resamples', 'api_url'],

        data: function () {
            return {
                filters_data: [],

                metric_name_table:'',
                isLoading: false,
                fullPage: true,
                components: [], 
                form: null,
                forms: [],
                charts: [],
                filters: [],
                periods: [],
                formSelected: null,
                list_data_charts: {
                    y: [],
                    y2: [],
                    y3: [],
                    y4: []
                }
            }
        },
        methods: {
            /*
                Series management works as follows:
                All the data of the series are stored in the list_data_charts dictionary, which in turn has 4 lists, one for each axis.
                Among the data of the series is the following:
                - Parameters for the api call
                - Object formed with data from the html form.
                - The data obtained from the call to the api required to make all the graphs.
                - A global index that corresponds to the position in the
                  table of characteristics of the series.
            */

            /*
                Add a new series taking the parameters of the html form.
                The structure to add the other data is added to the list_data_charts list.
                After adding the structure with its parameters and the form data,
                the function manageDataSeries is called.
            */
            addSerie(){


                // Add params data to list_data_charts
                this.isLoading = true
                const url = this.api_url
                const form = this.form
                const { date } = form

                //  Assemble dict parameters
                let filters = form.filters
                let params = {
                    id_component: form.component.id,
                    int_periodicity: form.period[0],
                    resample_method: form.resample[0],
                    start_date:moment(form.start_date).format('YYYY-MM-DD'),
                    end_date:moment(form.limit_date).format('YYYY-MM-DD')
                }

                //      Get filters
                let f = {}
                Object.entries(filters).map(function (el) { 
                    f[el[0]] = el[1][0]
                    
                })
                form.f = {...filters}


                //      Assemble final dict parameters
                params = {...params, ...f}

                //  Add to list of all data charts in the wished axis
                this.list_data_charts[form.axis].push({'parameters'       : params,
                                                       'form'             : form,
                                                       'chart'            : null,
                                                       'global_list_index': null})

                // Get the data for all series, here we add form and chart
                this.manageDataSeries()

                this.resetForm()

                // The form selected is the form used in histogram
                this.formSelected = this.list_data_charts[form.axis].length
  
            },

            /*
                Deletes a series from the series characteristics table, 
                if the deleted series is the first one on the axis 
                then recalculate the entire axis using the manageDataSeries function

                @param  {int} index Global index of a time serie to delete, 
                                    remember that global index
                                    is the position in the table of features series 
                @return {null}
            */
            deleteSerie(index){

                this.formSelected = 0

                // Delete from global list
                this.forms.splice(index, 1)
                this.charts.splice(index, 1)

                // Delete from list_data_charts with index
                var axis_to_recalculate = this.deleteFromListDataCharts(index)
                this.sustractGlobalIndex(index)

                // If we need recalculate a axis, then send this parameter to manageDataSeries
                if (axis_to_recalculate != null) {
                    this.manageDataSeries(axis_to_recalculate)
                } else {
                    this.manageDataSeries()
                }

            },

            /*
                It removes the data of a time series, 
                it also removes it from list_data_charts, 
                if it is the first in the list of its axis, 
                it returns the axis to be recalculated by the manageDataSeries function

                @param  {int} index Global index of a time serie to delete, 
                                    remember that global index
                                    is the position in the table of features series 
                @return {str} Name of axis that need be recalculated due to delete 
                              the first time serie in his axis     
            */
            deleteFromListDataCharts(index){

                // Delete from list_data_charts with index
                var axis_to_recalculate = null
                //      Iterate about axis names
                for (const axis_name in this.list_data_charts) {

                    // Iterate about all series in the axis list
                    for (const [i, ts_data] of this.list_data_charts[axis_name].entries()) {

                        // If the global index == to input index, delete
                        if (ts_data['global_list_index'] == index) {

                            this.list_data_charts[axis_name].splice(i, 1)

                            // If we delete the first time serie, get data from all
                            // series from axis, the multiplier would be different 
                            // therefore the values of time series be different too
                            // and for this we need calculate all again.
                            if (i == 0) {
                                axis_to_recalculate = axis_name
                            }
                            break
                        }                
                    }
                }

                return axis_to_recalculate

            },

            /*
                Subtract 1 from all the global indexes after a certain index, 
                used when a series is eliminated from the series characteristics table, 
                in which the indices cannot be the same as it would not correspond to the real position.
                Nor can everything be recalculated as this could change 
                the orders of the series in this table.

                @param  {int} index Global index of a time serie, 
                                    all global indexes after this indexes will be subtracted in one
                                    is the position in the table of features series
                @return {null}      
            */
            sustractGlobalIndex(index){
                for (const axis_name in this.list_data_charts) {

                    // Iterate about all series in the axis list
                    for (const [i, ts_data] of this.list_data_charts[axis_name].entries()) {

                        // Quit 1 to all global index forward to delete element
                        if (ts_data['global_list_index'] >= index){
                            this.list_data_charts[axis_name][i]['global_list_index']--
                        }                   
                    }
                }
            },

            /*
                This function manages the calculations, 
                organization and generation of graphs for all time series.
                It allows obtaining and managing the data of 
                new series and organizing them again when a time series 
                is eliminated by the user, 
                in which case all the time series of an axis must be recalculated.

                @param  {str} axis_to_recalculate Name of axis that need be recalculated
                @return {null}
            */
            async manageDataSeries(axis_to_recalculate=null){

                // If we need recalculate a axis, it will be enough with change the 'chart' value
                // in the data of every serie to null, this will cause the series to be recalculated
                if (axis_to_recalculate!=null) {
                    for (const [i, ts_data] of this.list_data_charts[axis_to_recalculate].entries()) {
                        this.list_data_charts[axis_to_recalculate][i]['chart'] = null
                    }
                }

                // Iterate about each axis 
                for (const axis_name in this.list_data_charts) {

                    // Iterate about each time serie in axis list
                    for (const [i, ts_data] of this.list_data_charts[axis_name].entries()) {

                        // if we add a serie in a axis for first time, dont sent symb multiplier
                        if (i == 0) {
                            var symbol_multiplier = null
                            
                        // In other case, send the multiplier from first time serie in the axis
                        // with this the time serie to calculate will have the same multiplier
                        // of the first time serie
                        } else {
                            var symbol_multiplier = (this.list_data_charts[axis_name][0].form
                                                                                        .response
                                                                                        .symbol_multiplier)
                        }

                        ts_data.parameters['symbol_multiplier'] = symbol_multiplier

                        // Get data and assemble chart only if this not have data
                        if (ts_data['chart'] == null) {

                            // Get the extra data of the time serie using, 
                            // here we get the chart data and other elements
                            var new_ts_data = await this.completeDataFormSerie(ts_data)

                            // With the got data we assemble the plotly chart and add to
                            // new_ts_data
                            new_ts_data['chart'] = this.assembleChart(new_ts_data['form'])

                            // Replace new_ts_data in list of data chars
                            this.list_data_charts[axis_name][i] = new_ts_data

                            // Assign a global index and add to global list only if we not are
                            // recalculating the axis
                            if (axis_to_recalculate == null) {

                                // Add too a index for know position of this in global forms
                                this.list_data_charts[axis_name][i]['global_list_index'] = this.forms.length

                                // Add to global list
                                this.forms.push(new_ts_data['form'])
                                this.charts.push(new_ts_data['chart'])

                            // If we are recalculating the axis, replace the new data
                            } else {

                                const global_index = this.list_data_charts[axis_name][i]['global_list_index']

                                // Replace new data in global list
                                this.forms[global_index] = new_ts_data['form']
                                this.charts[global_index] = new_ts_data['chart']
                            }
                        } else {}
                    
                    }
                }

                this.updateChart()
            },

            /*
                Complete the data required to graph a time series, 
                using the previously defined ts_data object, 
                it is possible to enter a symbol_multiplier multiplier in the ts_data
                if you want the consulted time series to have a specific multiplier

                @param  {Object} ts_data Object with structure and all data from a time serie
                                         for example parameters, chart, multiplier, 
                                         form and global index
                @return {Object} ts_data object with extra data got from api of mec
                                 this data contains required data for get chart, histogram,
                                 unit and etc
            */
            async completeDataFormSerie(ts_data){

                this.isLoading = true

                // Take params to send to api of ts_data
                const url = this.api_url
                const params = ts_data['parameters']


                try {
                    // Do query
                    const resp = await axios.get(url, {params})
                    const { data } = resp


                    if(typeof bar === 'string') {
                       data = JSON.parse(data)
                    }
                    

                    // Add data to ts_data object and return
                    ts_data.form.response = data
                    ts_data.form.unit = data.unit


                    this.isLoading = false

                    return ts_data

                } catch (err) {
                    this.isLoading = false
                    throw new Error(err); 
                
                }                

            },

            /*
                Assemble the object for plot this chart with plotly
                using the time serie data in form object

                @param  {Object} form Form of ts_data with all data of html form and response
                                      of api
                @return {Object} chart with required structure and info for plot with plotly

            */
            assembleChart(form){

                var data = form.response

                const x = data.time_array
                const y = data.values_array

                const chart = {
                    x,
                    y,
                    type: 'scatter',
                    side: 'right',
                    name: form.component.component,
                    mode: 'lines',
                    line: {'shape':'spline', 'smoothing':1.3},
                    opacity: 0.7,
                    textposition: 'bottom center',
                    hoverinfo: null,
                    stackgroup: null,
                    yaxis: form.axis,
                    unit: data.unit

                };

                return chart

            },
            onChangeMetric(event) {

        
                this.isLoading = true
                const metric_id = this.form.metric.pk
                const url = this.components_url

                this.form.filters = []

                const params = {
                    metric: metric_id
                }
        
                axios.post(url, params).then(({data}) =>{
                    const components = data.data
                    const periodicitys = data.avalaible_periodicitys

                    let filters = data.filters


                    this.metric_name_table = data.metric_name_table

                    filters = _.orderBy(filters, ['key'],['asc']); 
                    this.filters = filters


                    if(components.length){
                        this.form.component = components[0]
                    }       
                    this.components = components

                    if(periodicitys.length){
                        this.form.period = periodicitys[1]
                    }
                    this.periods = periodicitys               


                    this.isLoading = false
                })     

            },
            resetForm(){
                
                const from = new Date();

                from.setMonth(from.getMonth() - 3);
                this.form = {
                    f: {},
                    metric: null,
                    filters:[],
                    component: null,
                    date: [
                        from,
                        new Date(),
                    ],
                    period: this.periods[3],
                    resample: this.resamples[2],
                    axis: "y",
                    start_date: new Date(moment('2000-01-01')),
                    limit_date: new Date()
                }

            },
            histogram(){

                const form = this.forms[this.formSelected]
              
                if(form){

                    const {bin_edges, frecuency}  = form.response

                    var trace1 = {
                        x: bin_edges,
                        y: frecuency,
                        
                        type: 'bar'
                    };

                    var layout = {
                    
                        title:{
                            text:'Histograma de serie de tiempo seleccionada    ',
                            font: {
                                size: 24
                            },  
                        }
                    }



                    var data = [trace1];

                    Plotly.newPlot('histogramChart', data, layout);

                }else{
                
                    var trace1 = {
                        x: [],
                        y: [],
                        type: 'bar'
                    };

                    var layout = {
                        title:''
                    }

                }
               
                Plotly.newPlot('histogramChart', data, layout);

            },

            /*
                Plot all time series in list_data_charts in their respectives axis,
                using the unit of first time serie in each axis.

                @return {null}

            */
            updateChart(){

                // Update histogram
                this.histogram()

                // Get the title for each axis
                // using the unit of first time serie in each axis
                var y_title = ''
                var y2_title = ''
                var y3_title = ''
                var y4_title = ''

                if (this.list_data_charts.y.length > 0){
                    y_title = this.list_data_charts.y[0]['form']['response']['unit']
                };
                 
                if (this.list_data_charts.y2.length > 0){
                    y2_title = this.list_data_charts.y2[0]['form']['response']['unit']
                };

                if (this.list_data_charts.y3.length > 0){
                    y3_title = this.list_data_charts.y3[0]['form']['response']['unit']
                };

                if (this.list_data_charts.y4.length > 0){
                    y4_title = this.list_data_charts.y4[0]['form']['response']['unit']
                };

                // This object are a template for all axis
                var base_axis = {
                    exponentformat: 'power',
                    linewidth: 0.5, 
                    linecolor: 'black', 
                    mirror: false,
                    gridcolor: '#f3f4f3',
                    fixedrange: false,
                    showline: false,
                    zeroline: false,
                    automargin: true
                }

                // Add/replace parameteres to use in the base_axis template
                var yaxis1 = {
                    title: y_title,
                    position: 0.1                    
                }

                var yaxis2 = {
                    title: y2_title,
                    anchor: 'x',
                    overlaying: 'y',
                    side: 'right',
                    position: 0.9                    
                }         

                var yaxis3 = {
                    title: y3_title,
                    anchor: 'free',
                    overlaying: 'y',
                    side: 'left',
                    position: 0                    
                }

                var yaxis4 = {
                    title: y4_title,
                    anchor: 'free',
                    overlaying: 'y',
                    side: 'right',
                    position: 1                    
                }

                // Build the plotly layout, here we use the templates and specific data of each axis
                var layout = {
                   
                    title:{
                        text:'Gráfica de series',
                        font: {
                            size: 24
                        },  
                    },
                    colorway: ["#0261A1", '#FF4F00', '#375CB1', '#FF7400', '#FFF400', '#FF0056'],
                    xaxis: {
                        "title": "Fecha",
                        'showline':true, 
                        'linewidth':1, 
                        'linecolor':'black', 
                        'mirror':false,
                        "autorange": true,                                           
                        'rangeslider': {'visible': true}, 
                        'type': 'date',
                        domain: [0.1, 0.9]
                    },

                    yaxis:  Object.assign(yaxis1, base_axis),
                    yaxis2: Object.assign(yaxis2, base_axis),
                    yaxis3: Object.assign(yaxis3, base_axis),
                    yaxis4: Object.assign(yaxis4, base_axis),                    

                    paper_bgcolor: 'white',
                    plot_bgcolor: 'white',
                    font: {"family": 'Arial', "size": 12},
                    hovermode: "closest",
                    legend:{
                        x: -0.0228945952895,
                        y: -0.5,
                        orientation: "h",
                        yanchor: "bottom",
                    },
                    margin:{
                        r: 10,
                        t: 100,
                        b: 10,
                        l: 10
                    }    
                }

                // Configuration to allow export data in svg format
                var config = {
                    toImageButtonOptions: {
                    format: 'svg', // one of png, svg, jpeg, webp
                    filename: 'Planta que margina',
                    height: 600,
                    width: 700,
                    scale: 1 // Multiply title/legend/axis/canvas sizes by this factor
                    }
                }

                // Plot with plotly in the 'serieChart' element
                Plotly.newPlot('serieChart', this.charts, layout, config);

            },
            removeForm(index){
                
                this.formSelected = 0
                this.forms.splice(index, 1)
                this.charts.splice(index, 1)

                this.updateChart()

            },
            setFormSelected(index){
                this.formSelected = index
                this.histogram()

            },
            clearFilter(filter){
                
            },
            changeFilter(){
                
               this.isLoading = true

                const metric_id = this.form.metric.pk
                const url = this.components_url

                let filters = this.form.filters
                
                filters = Object.entries(filters).map(function (el) { 
                    if(el){

                        if(el[0] && !!el[1]){
                            return [el[0], el[1][0]]                      
                        }
                    } 
                    
                });

                filters = filters.filter(el => el)

               
                const params = {
                    metric: metric_id,
                    custom_filters: Object.fromEntries(filters)
                }

                axios.post(url, params).then(({data}) =>{
                    const components = data.data
                    let filters = data.filters

                    filters = _.orderBy(filters, ['key'],['asc']); 

                    this.filters = filters
                    this.isLoading = false

                })

            },
            
            /*
                Export ploted data using the api for generate the xlsx file

                @return {null}
            */
            exportData(){
                this.isLoading = true

                axios.post('/api/download_graphed_data', 
                    this.forms, { responseType: "blob"}).then((response) => {
 
                    const url = window.URL.createObjectURL(new Blob([response.data]));
                    const link = document.createElement('a');
                    link.href = url;
                    link.setAttribute('download', 'datos_consulta_mec.xlsx');
                    document.body.appendChild(link);
                    link.click();

                });

                this.isLoading = false

            },
            
        },
        mounted() {
 
        },
        created(){
            this.resetForm()
        },
        filters: {
            moment: function (date) {
                return moment(date).format('YYYY-MM-DD');
            },
            pretty:function (name){

                var texts = {
                    'fuel_id': 'Combustible',
                    'resource_name': 'Recurso',
                    'shipping_type': 'Tipo de envio',
                    'generation_type': 'Generación',
                    'agent_detail': 'Agente',
                    'agent_activity': 'Actividad',
                    'ciiu_id': 'Ciiu',
                    'subactivity_id': 'Subactividad',
                    'river_id': 'Rio',
                    'hydrological_region_id': "Region hidroeléctrica"

                    };

                return texts[name] || name
            },
            toFixed: function (value) {
                if(value){
                    return value.toFixed(2)
                }
                return ''
            }
        },

        components: { DatePicker, Loading, vSelect },
    }
</script>


