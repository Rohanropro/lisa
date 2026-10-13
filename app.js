const $ = (s, root=document) => root.querySelector(s);
const $$ = (s, root=document) => [...root.querySelectorAll(s)];

const initialRecords = [
 {year:2081,district:"Chitwan",region:"Terai",crop:"Rice",area:120.5,production:652.3},
 {year:2081,district:"Sunsari",region:"Terai",crop:"Maize",area:98.2,production:521.7},
 {year:2081,district:"Jhapa",region:"Terai",crop:"Wheat",area:76.4,production:384.6},
 {year:2081,district:"Kaski",region:"Hill",crop:"Potato",area:65.7,production:298.4},
 {year:2081,district:"Bardiya",region:"Terai",crop:"Sugarcane",area:112.3,production:607.7},
 {year:2080,district:"Dolakha",region:"Mountain",crop:"Barley",area:42.6,production:102.2},
 {year:2079,district:"Kavre",region:"Hill",crop:"Millet",area:58.1,production:154.9},
 {year:2078,district:"Morang",region:"Terai",crop:"Rice",area:140.2,production:721.4}
];
let records = initialRecords.map(r=>({...r}));
let charts = {};
const colors = {green:"#25875c",blue:"#3988d9",orange:"#e5a32d",red:"#e36c64",purple:"#8969c8",teal:"#3b9b91",muted:"#9bb6a5"};
const gridColor = "#edf2ee";
Chart.defaults.font.family = "Inter, Arial, sans-serif";
Chart.defaults.font.size = 10;
Chart.defaults.color = "#829188";
Chart.defaults.plugins.legend.labels.usePointStyle = true;
Chart.defaults.plugins.legend.labels.boxWidth = 7;
Chart.defaults.plugins.legend.labels.padding = 16;

function chart(id, config) {
  const canvas = document.getElementById(id);
  if (!canvas) return;
  if (charts[id]) charts[id].destroy();
  charts[id] = new Chart(canvas, config);
}
function lineConfig(labels, datasets, extra={}) {
  return {type:"line",data:{labels,datasets:datasets.map((d,i)=>({ ...d,borderColor:d.color||Object.values(colors)[i],backgroundColor:d.color||Object.values(colors)[i],borderWidth:2,pointRadius:2.5,pointHoverRadius:5,tension:.34,fill:false }))},options:{responsive:true,maintainAspectRatio:false,interaction:{mode:"index",intersect:false},plugins:{legend:{position:"top",align:"start"}},scales:{x:{grid:{display:false},border:{display:false}},y:{beginAtZero:true,grid:{color:gridColor},border:{display:false},ticks:{maxTicksLimit:5}},...(extra.scales||{})},...extra.options}};
}
function barConfig(labels,datasets, horizontal=false) {
 return {type:"bar",data:{labels,datasets:datasets.map((d,i)=>({...d,backgroundColor:d.color||Object.values(colors)[i],borderRadius:5,borderSkipped:false,maxBarThickness:horizontal?18:34}))},options:{indexAxis:horizontal?"y":"x",responsive:true,maintainAspectRatio:false,plugins:{legend:{display:datasets.length>1,position:"top",align:"start"}},scales:{x:{grid:{display:!horizontal,color:gridColor},border:{display:false},ticks:{font:{size:9}}},y:{beginAtZero:true,grid:{display:horizontal?false:true,color:gridColor},border:{display:false},ticks:{font:{size:9}}}}}};
}
function doughnutConfig(labels,data) {
 return {type:"doughnut",data:{labels,datasets:[{data,backgroundColor:[colors.orange,colors.blue,colors.green],borderWidth:0,hoverOffset:5}]},options:{responsive:true,maintainAspectRatio:false,cutout:"68%",plugins:{legend:{display:false}}}};
}
function initCharts(){
 const years=["2072/73","2073/74","2074/75","2075/76","2076/77","2077/78","2078/79","2079/80","2080/81","2081/82"];
 chart("trendChart",lineConfig(years,[
  {label:"Rice",data:[390,425,402,455,418,437,420,475,449,493],color:colors.green},
  {label:"Maize",data:[198,221,230,240,238,259,257,286,278,295],color:colors.orange},
  {label:"Wheat",data:[119,139,137,151,145,164,177,169,180,195],color:colors.blue},
  {label:"Potato",data:[64,81,73,88,77,96,94,83,87,99],color:colors.purple},
  {label:"Sugarcane",data:[28,44,39,52,48,57,49,61,56,69],color:colors.red}
 ]));
 chart("regionChart",doughnutConfig(["Mountain","Hill","Terai"],[18.4,45.7,35.9]));
 chart("districtChart",barConfig(["Jhapa","Sunsari","Chitwan","Bardiya","Kaski"],[{label:"Yield (MT/ha)",data:[5.2,4.8,4.5,4.2,3.9],color:"#64aa86"}],true));
 chart("climateChart",lineConfig(["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"],[
  {label:"Rainfall (mm)",data:[24,35,52,78,166,255,310,338,299,127,68,39],color:colors.blue},
  {label:"Temperature (°C)",data:[12,14,16,18,21,23,24,24,23,21,17,13],color:colors.red},
  {label:"Illustrative yield index",data:[2.2,2.8,3.2,3.3,3.4,4.8,5.8,6.0,5.4,4.9,4.2,3.6],color:colors.green}
 ],{scales:{y:{beginAtZero:true,grid:{color:gridColor},border:{display:false}}}}));
 chart("regionalBarChart",barConfig(["Rice","Maize","Wheat","Potato","Sugarcane"],[
  {label:"Mountain",data:[55,32,42,31,10],color:colors.orange},
  {label:"Hill",data:[120,78,69,85,24],color:colors.blue},
  {label:"Terai",data:[230,142,99,63,180],color:colors.green}
 ]));
 chart("regionalDonut",doughnutConfig(["Mountain","Hill","Terai"],[18.4,45.7,35.9]));
 chart("environmentChart",lineConfig(["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"],[
  {label:"Mean temperature (°C)",data:[12,14,16,18,21,23,24,24,23,21,17,13],color:colors.red},
  {label:"Mean humidity (%)",data:[58,55,57,61,68,78,85,87,82,74,67,61],color:colors.green}
 ]));
 chart("seasonChart",barConfig(["Winter","Spring","Summer","Monsoon","Autumn"],[{label:"Rainfall (mm)",data:[62,248,612,1245,176],color:colors.blue}]));
}
function getFilters(){
 return {region:$("#regionFilter")?.value||"All",crop:$("#cropFilter")?.value||"All",year:$("#yearFilter")?.value||"All",search:($("#globalSearch")?.value||"").toLowerCase().trim()};
}
function filteredRecords(){
 const f=getFilters();
 return records.filter(r=>(f.region==="All"||r.region===f.region)&&(f.crop==="All"||r.crop===f.crop)&&(f.year==="All"||String(r.year)===f.year)&&(!f.search||[r.crop,r.district,r.region,String(r.year)].some(v=>String(v).toLowerCase().includes(f.search))));
}
function fmt(n){return Number(n).toLocaleString("en-US",{maximumFractionDigits:1});}
function recordRow(r,idx,withAction=false){
 const yieldVal=r.area>0?r.production/r.area:0;
 return `<tr><td>${r.year}</td><td>${escapeHTML(r.district)}</td><td>${r.region}</td><td><span class="crop-pill">${r.crop}</span></td><td>${fmt(r.area)}</td><td>${fmt(r.production)}</td><td>${yieldVal.toFixed(2)}</td>${withAction?`<td><button class="row-delete" data-delete="${idx}">Remove</button></td>`:""}</tr>`;
}
function escapeHTML(s){return String(s).replace(/[&<>"']/g,c=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[c]));}
function renderTables(){
 const data=filteredRecords();
 $("#recentTable").innerHTML=data.slice(0,5).map(r=>recordRow(r)).join("")||`<tr><td colspan="7">No records match your filters.</td></tr>`;
 const search=($("#tableSearch")?.value||"").toLowerCase();
 const crop=$("#tableCropFilter")?.value||"All";
 const all=records.map((r,i)=>({...r,_i:i})).filter(r=>(crop==="All"||r.crop===crop)&&(!search||[r.crop,r.district,r.region,String(r.year)].some(v=>String(v).toLowerCase().includes(search))));
 $("#allRecordsTable").innerHTML=all.map(r=>recordRow(r,r._i,true)).join("")||`<tr><td colspan="8">No records found.</td></tr>`;
 $("#recordCount").textContent=`Showing ${all.length} of ${records.length} session records`;
 $("#kpiRecords").textContent=fmt(6930 + records.length - initialRecords.length);
 $("#adminRecordCount").textContent=records.length;
 $("#kpiCrops").textContent=new Set(records.map(r=>r.crop)).size;
}
function showPage(name){
 $$(".page-view").forEach(p=>p.classList.toggle("active",p.id===`page-${name}`));
 $$(".nav-item[data-page]").forEach(b=>b.classList.toggle("active",b.dataset.page===name));
 const labels={dashboard:"Dashboard",regional:"Regional Comparison",environment:"Environmental Analysis",prediction:"Yield Prediction",data:"Data Management",admin:"Administrator"};
 $("#crumb").textContent=labels[name]||"Dashboard";
 $("#sidebar").classList.remove("open");
 window.scrollTo({top:0,behavior:"smooth"});
}
function toast(msg){
 const el=$("#toast");el.textContent=msg;el.classList.add("show");
 clearTimeout(toast.timer);toast.timer=setTimeout(()=>el.classList.remove("show"),2600);
}
function exportCSV(rows,name="agri-nepal-demo.csv"){
 const headers=["Year (BS)","District","Region","Crop","Area (ha)","Production (MT)","Yield (MT/ha)"];
 const body=rows.map(r=>[r.year,r.district,r.region,r.crop,r.area,r.production,(r.production/r.area).toFixed(2)]);
 const csv=[headers,...body].map(row=>row.map(v=>`"${String(v).replace(/"/g,'""')}"`).join(",")).join("\r\n");
 const blob=new Blob(["\ufeff"+csv],{type:"text/csv;charset=utf-8;"});
 const url=URL.createObjectURL(blob);const a=document.createElement("a");a.href=url;a.download=name;a.click();URL.revokeObjectURL(url);
 toast("CSV export downloaded.");
}
function updatePrediction(){
 const area=Number($("#predArea").value),prod=Number($("#predProduction").value);
 if(!(area>0)||!(prod>=0)){toast("Enter a positive area and a valid production value.");return;}
 $("#yieldResult").innerHTML=`${(prod/area).toFixed(2)} <small>MT/ha</small>`;
 $("#resultCrop").textContent=$("#predCrop").value;
 $("#resultDistrict").textContent=$("#predDistrict").value;
 $("#resultArea").textContent=`${fmt(area)} ha`;
 $("#resultProduction").textContent=`${fmt(prod)} MT`;
 $("#yieldExplanation").textContent="Calculated yield = production ÷ area. This is a derived value, not a future forecast.";
}
function openModal(){$("#recordModal").classList.add("open");}
function closeModal(){$("#recordModal").classList.remove("open");}
function addRecord(e){
 e.preventDefault();
 const area=Number($("#newArea").value),production=Number($("#newProduction").value);
 if(!(area>0)||!(production>=0)){toast("Please enter valid area and production values.");return;}
 records.unshift({year:Number($("#newYear").value),district:$("#newDistrict").value.trim(),region:$("#newRegion").value,crop:$("#newCrop").value,area,production});
 renderTables();closeModal();$("#recordForm").reset();toast("Demo record added for this session.");
}
$("#mainNav").addEventListener("click",e=>{const b=e.target.closest("[data-page]");if(b)showPage(b.dataset.page);});
document.addEventListener("click",e=>{
 const goto=e.target.closest("[data-goto]");if(goto)showPage(goto.dataset.goto);
 const del=e.target.closest("[data-delete]");if(del){records.splice(Number(del.dataset.delete),1);renderTables();toast("Demo record removed.");}
});
$("#openMenu").addEventListener("click",()=>$("#sidebar").classList.add("open"));
$("#closeMenu").addEventListener("click",()=>$("#sidebar").classList.remove("open"));
$("#topAdmin").addEventListener("click",()=>showPage("admin"));
["regionFilter","cropFilter","yearFilter","seasonFilter","globalSearch"].forEach(id=>$("#"+id).addEventListener(id==="globalSearch"?"input":"change",renderTables));
$("#tableSearch").addEventListener("input",renderTables);
$("#tableCropFilter").addEventListener("change",renderTables);
$("#addRecordBtn").addEventListener("click",openModal);
$("#closeModal").addEventListener("click",closeModal);
$("#cancelModal").addEventListener("click",closeModal);
$("#recordModal").addEventListener("click",e=>{if(e.target.id==="recordModal")closeModal();});
$("#recordForm").addEventListener("submit",addRecord);
$("#predictionForm").addEventListener("submit",e=>{e.preventDefault();updatePrediction();toast("Illustrative yield calculated.");});
$("#trendPeriod").addEventListener("change",()=>{
 const n=Number($("#trendPeriod").value);
 const c=charts.trendChart;if(!c)return;
 c.data.labels=c.data.labels.slice(-n);c.data.datasets.forEach(d=>d.data=d.data.slice(-n));c.update();
});
$("#exportBtn").addEventListener("click",()=>exportCSV(filteredRecords(),"dashboard-demo.csv"));
$("#dataExport").addEventListener("click",()=>exportCSV(records));
$("#regionalExport").addEventListener("click",()=>exportCSV(records,"regional-demo.csv"));
$("#climateExport").addEventListener("click",()=>{toast("Climate table is a field guide; no raw climate dataset is connected.");});
document.addEventListener("keydown",e=>{if(e.key==="Escape"){closeModal();$("#sidebar").classList.remove("open");}});
initCharts();renderTables();updatePrediction();
