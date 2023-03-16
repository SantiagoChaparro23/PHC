<template>

     <div class="row">

         <loading :active="isLoading"
                 :can-cancel="true"  
                 :is-full-page="fullPage"/>
                 
        <div class="col-md-4">
            <div class="card">
               
                <div class="card-body">

                    <div class="row">   
                        <div class="col-md-12">


                            <h4>Parámetros</h4>

                            <div class="form-group">
                              
                                <label for="">Nombre del proyecto:</label>
                                <select  placeholder='select' v-model="form.project" @change="onChangeProject($event)"  class="form-control ">
                                    <option value="" disabled selected>Seleccione</option>
                                    <option :value="project" v-for="(project, i) in projects" :key="i">{{project.fields.name}}</option>
                                </select>
                            </div>

                            <div class="row">
                                <div class="col-md-6">
                                    <div class="form-group">
                                        <label for="">Base de datos del caso base:</label>
                                        <select v-model="form.base_db" class="form-control ">
                                            <option :value="db" v-for="(db, i) in dbs" :key="i">{{db.name}}</option>
                                        </select>
                                        <!-- <small if='errors.base_db' class='text-danger'>Este campo es querido</small> -->
                                    </div>
                                </div>
                                <div class="col-md-6">
                                     <div class="form-group">
                                        <label for="">Base de datos del proyecto</label>
                                        <select v-model="form.db"  @change="onChangeDb($event)" class="form-control">
                                            <option :value="db" v-for="(db, i) in dbs" :key="i">{{db.name}}</option>
                                        </select>
                                    </div>

                                </div>
                            </div>

                            <div class="form-group">
                                <label for="">Planta</label>
                                <input v-model="form.plant" type="text" class="form-control "> 
                            </div>



                            <div class="form-group">
                                <label for="">Año del calculo</label>
                                <input v-model="form.year" type="text" class="form-control" placeholder="Año del calculo"> 
                            </div>



                             <div class="form-group">
                                <label for="">TRM</label>
                                <input v-model="form.trm" type="text" class="form-control" placeholder="TRM"> 
                            </div>


                            <div class="form-group">
                                <label for="">Factor de demanda</label> <br>
                                
                                <input v-model="form.demand_factor" type="text" class="form-control" placeholder="Factor de demanda"> 
                            </div>



                            <div class="row">
                                <div class="col-md-6">
                                    <div class="form-group">
                                        <label for="">Fecha de entrada en operacion:</label> <br>
                                        <date-picker v-model="form.start_date"></date-picker>
                                        <!-- <input v-model="form.start_date" type="text" class="form-control" placeholder="Fecha de entrada en operacion">  -->
                                    </div>
                                </div>
                                <div class="col-md-6">
                                     <div class="form-group">
                                        <label for="">Fecha limite de operacion</label>
                                        <date-picker v-model="form.limit_date" ></date-picker>
                                        <!-- <input v-model="form.limit_date" type="text" class="form-control" placeholder="Fecha limite de operacion">  -->
                                    </div>
                                </div>
                            </div>



                            

                            



                            <div class="form-group mt-1">
                                <label for="">Tabla de tasas reconocidas:</label>
                                <button @click="addRate" class='btn btn-sm btn-info float-right'><i class="far fa-plus-square"></i></button>
                                <table class="table table-sm table-borderless mt-2">
                                    <thead>
                                        <tr>
                                            <th>Año</th>
                                            <th>Tasa reconocida</th>
                                            <th></th>
                                        </tr>
                                    </thead>
                                    <tbody>
                                        <tr v-for="(rate, i) in r" :key="i">
                                            <td>
                                                <input type="number" v-model='rate.year' class="form-control">
                                            </td>
                                            <td>
                                                <input type="number" v-model='rate.value' class="form-control">
                                            </td>
                                            <td class='text-right'>
                                                <button @click="onRemoveRate(i)" class='btn btn-sm btn-danger mt-1'><i class="fas fa-trash"></i></button>
                                            </td>
                                        </tr>
                                    </tbody>
                                </table>
                            </div>

                            <p v-if='error' class='text-danger'>Hay campos incompletos</p>
                            <button @click='calculate' class='btn btn-success btn-block'>Calcular Beneficios</button>
                            <!-- <button :disabled="!form.component" @click="addSerie" class='btn btn-success btn-block'>Agregar Serie</button> -->
                            
                        </div>
                    </div>
                    
                </div>
            </div>
        </div>
        <div class="col-md-8">
            
            <div class="card" >      
                <div class="card-body">


                    <p class='text-center p-5' v-if='isEmpty'>
                        <img src="/static/images/illustrations/empty.svg" width="200" class='mb-2'> <br>
                        Usa los filtros para calcular los beneficios
                    </p>

                    <div id="myDiv1"></div>
                    <div id="myDiv2"></div>
                    <div id="myDiv3"></div>
                    <div id="myDiv4"></div>
                    <div id="myDiv5"></div>
                    <div id="myDiv6"></div>

                    <div id="myDiv7"></div>
                    <div id="myDiv8"></div>
                    <div id="myDiv9"></div>
                    <div id="myDiv10"></div>
<!-- 
                    <button v-show='this.data' @click="exportData" class='btn btn-success btn-block'>Exportar resultados</button>
 -->
                    <button @click="exportData" class='btn btn-success btn-block'>Exportar resultados</button>                    
                    
                </div>
            </div>
        </div>
        
     </div>
    
</template>

<script>
    import DatePicker from 'vue2-datepicker';
    import Loading from 'vue-loading-overlay';
    
    import 'vue-loading-overlay/dist/vue-loading.css';
    import 'vue2-datepicker/index.css';
    import moment from 'moment';


    export default {
        props: ['projects', 'get_dbs_url', 'get_operationalbenefits_url', 'rates'],
        data: function () {
            return {
                isLoading: false,
                fullPage: true,
                components: [], 
                form: null,
                dbs:[],
                r:[],
                data: null,
                error: false,
                isEmpty: true
            }
        },
        methods: {
            calculate(){
                this.error = false

                if(!this.form.project || !this.form.base_db || !this.form.db){
                    this.error = true
                }

                this.data = {
                    project_id: this.form.project.pk,
                    base_db: this.form.base_db.id,
                    db: this.form.db.id,
                    plant: this.form.plant,
                    trm: this.form.trm,
                    year: this.form.year,
                    demand_factor: this.form.demand_factor,
                    start_date: moment(this.form.start_date).format("YYYY-MM-DD"),
                    limit_date: moment(this.form.limit_date).format("YYYY-MM-DD"),
                    rates: this.rates,

                }

                this.config = {
                    toImageButtonOptions: {
                    format: 'svg', // one of png, svg, jpeg, webp
                    height: 600,
                    width: 1000,
                    scale: 1, // Multiply title/legend/axis/canvas sizes by this factor
                    responsive: true
                    }
                };

                const url = this.get_operationalbenefits_url

                this.isLoading = true

                axios.post(url, this.data).then(({data}) =>{

                    console.log(data)

                    // Charts
                    this.isEmpty = false
                    this.makeChart1(data.graphics.histogram_of_operating_profit_graph,
                                    data.graphics.histogram_of_operating_profit_annotation)

                    this.makeChart2_3(data.graphics.average_profits_per_demand_block, 
                                      data.graphics.average_delta_marginal_cost_per_block_of_demand)

                    this.makeChart4_5(data.graphics.marginal_cost_without_project, 
                                      data.graphics.marginal_cost_with_project)

                    this.makeChart6(data.graphics.generation_plant)

                    // Tables
                    this.makeAllTables(data.tables)

                this.hiddenLabels = false

                this.isLoading = false
                   
                })
              
            },
            makeChart1(data_chart1, data_annotation1){

                var trace1 = {
                    type: 'bar',
                    x: data_chart1.class,
                    y: data_chart1.frecuency,
                    name: "Frecuencia",
                    marker: {'color':'#0464a4'},
                    xaxis: 'x1',
                    yaxis: 'y1'
                };

                var trace2 = {
                    type: 'scatter',
                    x: data_chart1.class,
                    y: data_chart1.accumulated_percentage,
                    mode: 'lines+markers',
                    opacity: 0.7,
                    marker: {
                        color: 'green'
                    },
                    line: {shape: 'spline', 
                           smoothing: 1.3, 
                           width: 2
                    },
                    name: "Porcentaje acumulado",
                    xaxis: 'x1',
                    yaxis: 'y2'
                };

                var table = this.makeTable(data_annotation1, ['95 PSS', 'MEDIANA', '05 PSS']);
                table['xaxis'] = 'x3'
                table['yaxis'] = 'y3'
                table['domain'] = {x: [0.1, 0.9], y: [0, 0.15]}


                var data = [trace1, trace2, table];
                       

                var layout = { 
                    title: 'Histograma de beneficios operativos',
                    xaxis_type: 'category',
                    paper_bgcolor: 'white',
                    plot_bgcolor: 'white',
                    title_x: 0.5,
                    font: {
                        family: 'Arial', 
                        size: 12
                    },
                    hovermode: "closest",
                    legend:{
                        // x: -0.0228945952895,
                        // y: -0.189563896463,
                        orientation: "h",
                        yanchor: "top",
                    },

                    // Xaxis ---
                    xaxis1: {
                        domain: [0, 1], 
                        anchor: 'y1', 
                        showticklabels: false,
                        title: "Miles de Millones de Pesos",
                        autorange: true,
                        type: "category",
                        showline: false,
                        zeroline: false,
                        linewidth:1, 
                        linecolor:'black', 
                        mirror:false,
                        gridcolor: 'white'
                    },

                    xaxis3: {
                        domain: [0, 1], 
                        anchor: 'y3', 
                        showticklabels: false  
                    },

                    // Yaxis ---
                    yaxis1:{
                        title: 'Frecuencia', 
                        showline: false,
                        zeroline: false,
                        linewidth: 0.5, 
                        linecolor: 'black', 
                        mirror: true,
                        gridcolor: '#f3f4f3',
                        domain: [0.33, 1], 
                        anchor: 'x1'
                    },
                    yaxis2:{
                        showline: false,
                        zeroline: false,
                        showgrid: false,                     
                        title: '%',
                        side: 'right',
                        overlaying: 'y1'
                    },

                    yaxis3: {domain: [0, 0.015], anchor: 'x3'},

                    height: 600
                };

                Plotly.newPlot('myDiv1', data, layout, this.config);

            },

            makeChart2_3(data_chart2, data_chart3){

                var dct_colores = {
                    1: 'rgb(83, 127, 181)',
                    2: 'rgb(56, 165, 44)',
                    3: 'rgb(4, 95, 165)',
                    4: 'rgb(135, 98, 156)',
                    5: 'rgb(73, 170, 195)'
                };

                var month_list = ['Enero', 'Febrero', 'Marzo', 'Abril',
                                  'Mayo', 'Junio', 'Julio', 'Agosto',
                                  'Septiembre', 'Octubre', 'Noviembre', 'Diciembre']

                var base_layout = { 
                        barmode : 'group', 
                        xaxis : {
                            title: "Mes",
                            autorange: true,
                            type: "category",
                            showline: true, 
                            linewidth:1, 
                            linecolor:'black', 
                            mirror:false,
                            gridcolor: 'white'},                            
                        yaxis : {
                            showline:true, 
                            linewidth:0.5, 
                            linecolor:'black', 
                            gridcolor: '#f3f4f3'
                        },
                        paper_bgcolor : 'white',
                        plot_bgcolor : 'white',
                        title_x : 0.5,
                        // margin : margin,
                        hovermode : "closest",
                        legend : {
                            x: -0.0228945952895,
                            y: -0.189563896463,
                            orientation: "h",
                            yanchor: "top",
                        },                                                
                        font : {
                            family: 'Arial', 
                            size: 12
                        }
                };


                // Chart 2
                var data = this.build_traces_chart_2_3(data_chart2, month_list, dct_colores)

                var layout = base_layout;
                layout['title'] = 'Promedio de Beneficios por Bloque de demanda';
                layout['yaxis']['title'] = 'Miles de Millones de COP';

                Plotly.newPlot('myDiv2', data, layout, this.config);


                // Chart 3
                var data = this.build_traces_chart_2_3(data_chart3, month_list, dct_colores)

                var layout = base_layout;
                layout['title'] = 'Promedio Delta costo marginal por Bloque de demanda';
                layout['yaxis']['title'] = 'COP/kWh';

                Plotly.newPlot('myDiv3', data, layout, this.config);          

            },

            build_traces_chart_2_3(data_chart, month_list, dct_colores){
                var data = [];
                for (let i = 1; i < Object.keys(data_chart).length + 1; i++) {

                    var trace = {
                        name: 'Bloque ' + i.toString(),
                        type: 'bar',
                        x: month_list,
                        y: data_chart[i],
                        marker: {
                            color: dct_colores[i],
                        }
                    };   

                    data.push(trace);
                        
                };

                return data

            },

            makeChart4_5(data_chart4, data_chart5){

                var dct_colores = {'Prom':'#0261A1', 'Q. Sup':'#ED7D31', 'Q. Inf':'#38A52B'}

                var base_layout = { 
                        barmode : 'group',
                        xaxis : {
                            title: "Año",
                            autorange: true,
                            showline: true, 
                            linewidth: 1, 
                            linecolor: 'black', 
                            mirror: false,
                            gridcolor: 'white',
                            tickangle : -90,
                            dtick : "M6",
                            tickformat : "%m/%Y",
                            showline: false,
                            zeroline: false
                        },
                        yaxis : {
                            title: 'USD/MWh',
                            showline: true,
                            linewidth: 0.5,
                            linecolor: 'black',
                            gridcolor: '#f3f4f3',
                            showline: false,
                            zeroline: false,                            
                        },
                        paper_bgcolor : 'white',
                        plot_bgcolor : 'white',
                        title_x : 0.5,
                        // margin : margin,
                        hovermode : "closest",
                        legend : {
                            "x": -0.0228945952895,
                            "y": -0.189563896463,
                            "orientation": "h",
                            "yanchor": "top",
                        },
                        font : {"family": 'Arial', "size": 12}
                };                

                // Chart 4
                var data = this.build_traces_chart_4_5(data_chart4, dct_colores)

                var layout = base_layout;
                layout['title'] = 'Costo marginal - Con proyecto';

                Plotly.newPlot('myDiv4', data, layout, this.config);

                // Chart 5
                var data = this.build_traces_chart_4_5(data_chart5, dct_colores)

                var layout = base_layout;
                layout['title'] = 'Costo marginal - Sin proyecto';

                Plotly.newPlot('myDiv5', data, layout, this.config);                 
        
            },
            build_traces_chart_4_5(data_chart, dct_colores){
                var data = [];
                for (let i = 0; i < Object.keys(data_chart).length; i++) {

                    var name_col = Object.keys(data_chart)[i]
                    if (name_col != 'date'){

                        var trace = {
                            name: name_col,
                            type: 'scatter',
                            x: data_chart.date,
                            y: data_chart[name_col],
                            marker: {
                                color: dct_colores[name_col],
                            }
                        };
                        data.push(trace);      
                    }
                };
                return data

            },

            makeChart6(data_chart6){

                var trace = {
                    type: 'scatter',
                    x: data_chart6.date,
                    y: data_chart6.value,
                    marker: {
                        color: '#0261A1',
                        line: {
                            width: 2.5
                        }
                    }
                };                

                var data = [trace];

                var layout = { 
                        barmode : 'group', 
                        xaxis : {
                            title : "Año",
                            autorange : true,
                            showline : true, 
                            linewidth : 1, 
                            linecolor : 'black', 
                            mirror : false,
                            gridcolor : 'white',
                            tickangle : -90,
                            dtick : "M6",
                            tickformat : "%m/%Y"                         
                        },
                        yaxis : {
                            title : 'GWh',
                            showline : true, 
                            linewidth : 0.5, 
                            linecolor :'black', 
                            gridcolor : '#f3f4f3',
                            showline: false,
                            zeroline: false                            
                        },
                        paper_bgcolor : 'white',
                        plot_bgcolor : 'white',
                        title : 'Generación planta ' + this.data.plant,
                        title_x : 0.5,
                        hovermode : "closest",
                        legend : {
                            x : -0.0228945952895,
                            y : -0.189563896463,
                            orientation : "h",
                            yanchor : "top",
                        },                         
                        font : {"family": 'Arial', "size": 12}                          
                };

                Plotly.newPlot('myDiv6', data, layout, this.config);
               
            },

            makeAllTables(data_tables){

                var base_layout = {
                    // height: 500,
                    margin:{
                        l: 0,
                        r: 0,
                        u: 0,
                        b: 0
                    }     
                };

                var table1 = this.makeTable(data_tables.vpn, ['Año', '05PSS', 'Mediana', '95PSS']);
                var layout1 = base_layout;
                layout1['height'] = 200;
                layout1['title'] = 'VPN';
                Plotly.newPlot('myDiv7', [table1], layout1, this.config);                

                var table2 = this.makeTable(data_tables.annuity_benefits, ['Año', '05PSS', 'Mediana', '95PSS']);
                var layout1 = base_layout;
                layout1['height'] = 1000;                
                layout1['title'] = 'Anualidad beneficios';
                Plotly.newPlot('myDiv8', [table2], base_layout, this.config);

                var table3 = this.makeTable(data_tables.average_marginal_cost, ['Año', 'Sin proyecto', 'Con proyecto']);
                var layout1 = base_layout;
                layout1['height'] = 1000;                
                layout1['title'] = 'Costo Marginal Promedio [USD/MWh]';
                Plotly.newPlot('myDiv9', [table3], base_layout, this.config);

                var table4 = this.makeTable(data_tables.generation_plant, ['Año', 'Prom', 'Q. Sup', 'Q. Inf']);
                var layout1 = base_layout;
                layout1['height'] = 1000;                
                layout1['title'] = 'Generación planta';
                Plotly.newPlot('myDiv10', [table4], base_layout, this.config);                

            },
            makeTable(dict_data, headers){
                // We use headers for keep a wished order in table

                // Build list of columns with data
                var data = [];
                for (let i = 0; i < Object.keys(dict_data).length; i++) {

                    var key = Object.keys(dict_data)[i]
                    data.push(dict_data[key])

                };

                // Build list for alternate rowEvenColor and rowOddColor
                var rowOddColor = 'rgb(220, 230, 241)';
                var rowEvenColor = 'white';
                var colors_rows = [];
                for (let i = 0; i < data[0].length; i++) {

                    if (i%2 == 0){
                        colors_rows.push(rowEvenColor)
                    } else{
                        colors_rows.push(rowOddColor)
                    }
                };                

                var table = {
                    type: 'table',
                    header: {
                      values: headers,
                      align: ["center", "center"],
                      line: {color: "grey", width: 1},
                      fill: {color: ['rgb(4, 100, 164)']},
                      font: {family: "Droid Sans", size: 15, color: "white"}

                    },
                    cells: {
                      values: data,
                      align: ["center", "center"],
                      line: {color: "rgb(211, 211, 211)", width: 1},
                      height: 30,
                      fill: {color: [colors_rows]},
                      font: {family: "Droid Sans", size: 15, color: "rgb(90, 90, 90)"}
                    },
                    domain: {x: [0, 1], y: [0, 1]}
                }
                return table

            },


            resetForm(){

               this.form =  {
                    project:'',
                    base_db:null,
                    db:null,
                    year:new Date().getFullYear(),
                    trm:null,
                    demand_factor :null,
                    start_date : null,
                    limit_date :null,
                    plant: ''
                }
            },
            addRate(){
                this.r.push({year: new Date().getFullYear(), value:0})
            },
            onRemoveRate(index){
                console.log(this.r)

                this.r.splice(index, 1);
            },
            onChangeDb(event){
                
                this.form.plant = this.form.db.plant || ''
            },
            onChangeProject(event) {

                this.isLoading = true
                const project = this.form.project

                const project_id = project.pk
                const url = this.get_dbs_url

                const {start_date, limit_date, trm, demand_factor} = project.fields
                console.log(`${start_date} 00:00:00`)
                console.log(new Date(`${start_date} 00:00:00`) )
                this.form.start_date = new Date(`${start_date} 00:00:00`) 
                this.form.limit_date = new Date(`${limit_date} 00:00:00`) 
                this.form.trm = trm
                this.form.demand_factor = demand_factor

                const params = {
                    project_id
                }
        
                axios.get(url, {params}).then(({data}) =>{
                    console.log(data)
                    this.dbs = data.dbs

                    this.isLoading = false
                })     

            },

            exportData(){
                console.log(this.data)

                this.isLoading = true

                axios.post('/sddp/operational-benefits/download-operationalbenefits', 
                    this.data, { responseType: "blob"}).then((response) => {

                    console.log(response)
                    console.log(response.data)
 
                    const url = window.URL.createObjectURL(new Blob([response.data]));
                    const link = document.createElement('a');
                    link.href = url;
                    link.setAttribute('download', 'beneficios_operativos.zip');
                    document.body.appendChild(link);
                    link.click();

                });

                this.isLoading = false
            }            

           
        },
        mounted() {
                this.r = this.rates
            
 
        },
        created(){
           this.resetForm()
        },
        filters: {
            moment: function (date) {
                return moment(date).format('MMMM Do YYYY');
            }
        },

        components: { DatePicker, Loading },
    }
</script>


