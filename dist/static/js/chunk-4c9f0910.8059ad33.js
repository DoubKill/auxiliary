(window["webpackJsonp"]=window["webpackJsonp"]||[]).push([["chunk-4c9f0910"],{"3c17":function(e,t,r){"use strict";r.d(t,"p",(function(){return a})),r.d(t,"o",(function(){return c})),r.d(t,"j",(function(){return l})),r.d(t,"i",(function(){return o})),r.d(t,"l",(function(){return s})),r.d(t,"e",(function(){return u})),r.d(t,"d",(function(){return p})),r.d(t,"m",(function(){return m})),r.d(t,"k",(function(){return g})),r.d(t,"n",(function(){return h})),r.d(t,"c",(function(){return d})),r.d(t,"f",(function(){return b})),r.d(t,"h",(function(){return f})),r.d(t,"g",(function(){return _})),r.d(t,"b",(function(){return S})),r.d(t,"a",(function(){return y}));var n=r("b775"),i=r("99b1");function a(e){return Object(n["a"])({url:i["a"].ValidateVersionsUrl,method:"get",params:e})}function c(e,t){return Object(n["a"])({url:i["a"].TankMaterialsUrl,method:"get",params:{equip_no:e,tank_type:t}})}function l(e){var t=arguments.length>1&&void 0!==arguments[1]?arguments[1]:null,r=arguments.length>2&&void 0!==arguments[2]?arguments[2]:{};if(t)var a=i["a"].RubberMaterialUrl+t+"/";else a=i["a"].RubberMaterialUrl;var c={url:a,method:e};return Object.assign(c,r),Object(n["a"])(c)}function o(e){var t=arguments.length>1&&void 0!==arguments[1]?arguments[1]:null,r=arguments.length>2&&void 0!==arguments[2]?arguments[2]:{};if(t)var a=i["a"].RubberMaterialCopyUrl+t+"/";else a=i["a"].RubberMaterialCopyUrl;var c={url:a,method:e};return Object.assign(c,r),Object(n["a"])(c)}function s(e){var t=arguments.length>1&&void 0!==arguments[1]?arguments[1]:null,r=arguments.length>2&&void 0!==arguments[2]?arguments[2]:{};if(t)var a=i["a"].RubberProcessStepUrl+t+"/";else a=i["a"].RubberProcessStepUrl;var c={url:a,method:e};return Object.assign(c,r),Object(n["a"])(c)}function u(e){var t=arguments.length>1&&void 0!==arguments[1]?arguments[1]:{},r={url:i["a"].EquipAllUrl,method:e};return Object.assign(r,t),Object(n["a"])(r)}function p(e){var t=arguments.length>1&&void 0!==arguments[1]?arguments[1]:{},r={url:i["a"].EquipCopyAllUrl,method:e};return Object.assign(r,t),Object(n["a"])(r)}function m(e){var t=arguments.length>1&&void 0!==arguments[1]?arguments[1]:{},r={url:i["a"].SiteUrl,method:e};return Object.assign(r,t),Object(n["a"])(r)}function g(e){var t=arguments.length>1&&void 0!==arguments[1]?arguments[1]:{},r={url:i["a"].RecipeNoUrl,method:e};return Object.assign(r,t),Object(n["a"])(r)}function h(e){var t=arguments.length>1&&void 0!==arguments[1]?arguments[1]:{},r={url:i["a"].StageUrl,method:e};return Object.assign(r,t),Object(n["a"])(r)}function d(e){var t=arguments.length>1&&void 0!==arguments[1]?arguments[1]:{},r={url:i["a"].DevTypeUrl,method:e};return Object.assign(r,t),Object(n["a"])(r)}function b(e){var t=arguments.length>1&&void 0!==arguments[1]?arguments[1]:{},r={url:i["a"].GlobalSITEUrl,method:e};return Object.assign(r,t),Object(n["a"])(r)}function f(e){var t=arguments.length>1&&void 0!==arguments[1]?arguments[1]:null,r=arguments.length>2&&void 0!==arguments[2]?arguments[2]:{};if(t)var a=i["a"].MaterialsUrl+t+"/";else a=i["a"].MaterialsUrl;var c={url:a,method:e};return Object.assign(c,r),Object(n["a"])(c)}function _(e){var t=arguments.length>1&&void 0!==arguments[1]?arguments[1]:{},r={url:i["a"].MaterialTypelUrl,method:e};return Object.assign(r,t),Object(n["a"])(r)}function S(e){var t=arguments.length>1&&void 0!==arguments[1]?arguments[1]:{},r={url:i["a"].ConditionUrl,method:e};return Object.assign(r,t),Object(n["a"])(r)}function y(e){var t=arguments.length>1&&void 0!==arguments[1]?arguments[1]:{},r={url:i["a"].ActionUrl,method:e};return Object.assign(r,t),Object(n["a"])(r)}},e521:function(e,t,r){"use strict";r.r(t);var n=function(){var e=this,t=e.$createElement,r=e._self._c||t;return r("div",{directives:[{name:"loading",rawName:"v-loading",value:e.loading,expression:"loading"}],attrs:{"element-loading-text":"加载中..."}},[r("br"),r("el-form",{attrs:{inline:!0}},[r("el-form-item",{attrs:{label:"机台"}},[r("el-select",{staticStyle:{width:"150px"},attrs:{size:"mini",clearable:"",placeholder:"请选择"},on:{"visible-change":e.SelectEquipDisplay,change:e.SelectEquipChange},model:{value:e.SelectEquip,callback:function(t){e.SelectEquip=t},expression:"SelectEquip"}},e._l(e.SelectEquipOptions,(function(e){return r("el-option",{key:e.id,attrs:{label:e.equip_name,value:e.id}})})),1)],1),r("el-form-item",{attrs:{label:"状态"}},[r("el-select",{staticStyle:{width:"150px"},attrs:{size:"mini",clearable:"",placeholder:"请选择"},on:{change:e.SelectRecipeStatusChange},model:{value:e.SelectRecipeStatus,callback:function(t){e.SelectRecipeStatus=t},expression:"SelectRecipeStatus"}},e._l(e.SelectRecipeStatusOptions,(function(e){return r("el-option",{key:e.value,attrs:{label:e.label,value:e.value}})})),1)],1),r("el-form-item",{attrs:{label:"产地"}},[r("el-select",{staticStyle:{width:"150px"},attrs:{size:"mini",clearable:"",placeholder:"请选择"},on:{"visible-change":e.SelectSiteDisplay,change:e.SelectSiteChange},model:{value:e.SelectSite,callback:function(t){e.SelectSite=t},expression:"SelectSite"}},e._l(e.SelectSiteOptions,(function(e){return r("el-option",{key:e.id,attrs:{label:e.global_name,value:e.id}})})),1)],1),r("el-form-item",{attrs:{label:"段次"}},[r("el-select",{staticStyle:{width:"150px"},attrs:{size:"mini",clearable:"",placeholder:"请选择"},on:{"visible-change":e.SelectStageDisplay,change:e.SelectStageChange},model:{value:e.SelectStage,callback:function(t){e.SelectStage=t},expression:"SelectStage"}},e._l(e.SelectStageOptions,(function(e){return r("el-option",{key:e.id,attrs:{label:e.global_name,value:e.id}})})),1)],1),r("el-form-item",{attrs:{label:"胶料编码"}},[r("el-input",{staticStyle:{width:"200px"},attrs:{size:"mini"},on:{input:e.input_rubber_noChanged},model:{value:e.input_rubber_no,callback:function(t){e.input_rubber_no=t},expression:"input_rubber_no"}})],1),r("br"),r("el-form-item",{staticStyle:{float:"right"}},[e.permissionObj.recipe.productbatching&&e.permissionObj.recipe.productbatching.indexOf("add")>-1?r("el-button",{attrs:{disabled:null===e.currentRow.stage_name},on:{click:e.CopyRecipeButton}},[e._v("复制新增")]):e._e()],1),r("el-form-item",{staticStyle:{float:"right"}},[e.permissionObj.recipe.productbatching&&e.permissionObj.recipe.productbatching.indexOf("add")>-1?r("el-button",{on:{click:e.AddRecipeButton}},[e._v("新增")]):e._e()],1)],1),r("el-table",{staticStyle:{width:"100%"},attrs:{"highlight-current-row":"",data:e.tableData,border:""},on:{"row-click":e.handleCurrentChange}},[r("el-table-column",{attrs:{align:"center",type:"index",width:"50",label:"No"}}),r("el-table-column",{attrs:{align:"center",width:"160%",prop:"stage_product_batch_no",label:"胶料配方编号"},scopedSlots:e._u([{key:"default",fn:function(t){return[r("el-link",{attrs:{type:"primary"},on:{click:function(r){return e.recipe_display_change(t.row)}}},[e._v(" "+e._s(t.row.stage_product_batch_no)+" ")])]}}])}),r("el-table-column",{attrs:{align:"center",prop:"product_name",label:"胶料名称"}}),r("el-table-column",{attrs:{align:"center",width:"200%",prop:"equip_name",label:"机台名称"}}),r("el-table-column",{attrs:{align:"center",width:"100%",prop:"equip_no",label:"机台编号"}}),e._e(),r("el-table-column",{attrs:{align:"center",width:"100%",prop:"dev_type_name",label:"炼胶机类型"}}),r("el-table-column",{attrs:{align:"center",prop:"used_type",label:"状态",formatter:e.usedTypeFormatter}}),r("el-table-column",{attrs:{fixed:"right",align:"center",label:"审核"},scopedSlots:e._u([{key:"default",fn:function(t){return[r("el-button-group",[1===t.row.used_type&&e.permissionObj.recipe.prod&&e.permissionObj.recipe.prod.indexOf("submit")>-1?r("el-button",{attrs:{size:"mini"},on:{click:function(r){return e.status_true(t.row)}}},[e._v(" 提交 ")]):e._e(),2===t.row.used_type&&e.permissionObj.recipe.prod&&e.permissionObj.recipe.prod.indexOf("using")>-1?r("el-button",{attrs:{size:"mini"},on:{click:function(r){return e.status_true(t.row)}}},[e._v(" 启用 ")]):e._e(),2===t.row.used_type&&e.permissionObj.recipe.prod&&e.permissionObj.recipe.prod.indexOf("using")>-1?r("el-button",{attrs:{size:"mini"},on:{click:function(r){return e.status_false(t.row)}}},[e._v(" 驳回 ")]):e._e(),4===t.row.used_type&&e.permissionObj.recipe.prod&&e.permissionObj.recipe.prod.indexOf("abandon")>-1?r("el-button",{attrs:{size:"mini"},on:{click:function(r){return e.status_false(t.row)}}},[e._v(" 废弃 ")]):e._e()],1)]}}])}),r("el-table-column",{attrs:{align:"center",prop:"batching_weight",label:"配料重量"}}),r("el-table-column",{attrs:{align:"center",prop:"production_time_interval",label:"炼胶时间"}}),r("el-table-column",{attrs:{align:"center",prop:"site_name",label:"site"}}),r("el-table-column",{attrs:{align:"center",prop:"stage_name",label:"段次"}}),r("el-table-column",{attrs:{align:"center",width:"100%",prop:"sp_num",label:"收皮(车/托)"}}),r("el-table-column",{attrs:{align:"center",width:"120%",prop:"created_username",label:"创建者"}}),r("el-table-column",{attrs:{align:"center",width:"180%",prop:"created_date",label:"创建时间"}}),r("el-table-column",{attrs:{align:"center",prop:"submit_username",label:"提交人"}}),r("el-table-column",{attrs:{align:"center",prop:"reject_username",label:"驳回人"}}),r("el-table-column",{attrs:{align:"center",prop:"used_username",label:"启用人"}}),r("el-table-column",{attrs:{align:"center",prop:"obsolete_username",label:"废弃人"}}),r("el-table-column",{attrs:{align:"center",prop:"batching_type",label:"配方来源",formatter:e.RecipeSourceFormatter}}),r("el-table-column",{attrs:{fixed:"right",align:"center",label:"操作"},scopedSlots:e._u([{key:"default",fn:function(t){return[r("el-button-group",[e.permissionObj.recipe.productbatching&&e.permissionObj.recipe.productbatching.indexOf("change")>-1?r("el-button",{attrs:{size:"mini",disabled:1!=t.row.used_type},on:{click:function(r){return e.ModifyRecipeButton(t.row)}}},[e._v("修改")]):e._e()],1)]}}])})],1),r("el-pagination",{attrs:{"current-page":e.currentPage,"page-size":e.pageSize,total:e.tableDataTotal,layout:"total, prev, pager, next"},on:{"update:currentPage":function(t){e.currentPage=t},"update:current-page":function(t){e.currentPage=t},"current-change":e.pagehandleCurrentChange}}),r("el-dialog",{attrs:{"close-on-click-modal":!1,"close-on-press-escape":!1,title:"复制新增配方",visible:e.dialogCopyRecipeSync},on:{"update:visible":function(t){e.dialogCopyRecipeSync=t}}},[r("el-form",{ref:"copyForm",attrs:{model:e.copyForm,inline:!0,rules:e.rules}},[r("el-form-item",{attrs:{label:"选择机台",prop:"CopySelectEquip"}},[r("el-select",{staticStyle:{width:"300px"},attrs:{size:"mini",clearable:"",placeholder:"请选择"},on:{change:e.SelectCopyEquipChange},model:{value:e.copyForm.CopySelectEquip,callback:function(t){e.$set(e.copyForm,"CopySelectEquip",t)},expression:"copyForm.CopySelectEquip"}},e._l(e.SelectCopyEquipOptions,(function(e){return r("el-option",{key:e.id,attrs:{label:e.equip_name,value:e.id}})})),1)],1),r("br"),r("el-form-item",{attrs:{label:"产地",prop:"site"}},[r("el-select",{staticStyle:{width:"150px"},attrs:{size:"mini",clearable:"",placeholder:"请选择"},on:{"visible-change":e.SelectSiteDisplay},model:{value:e.copyForm.site,callback:function(t){e.$set(e.copyForm,"site",t)},expression:"copyForm.site"}},e._l(e.SelectSiteOptions,(function(e){return r("el-option",{key:e.id,attrs:{label:e.global_name,value:e.id}})})),1)],1),r("el-form-item",{attrs:{label:"SITE",prop:"SITE"}},[r("el-select",{staticStyle:{width:"100px"},attrs:{size:"mini",clearable:"",placeholder:"请选择"},on:{"visible-change":e.SelectGlobalSITEDisplay},model:{value:e.copyForm.SITE,callback:function(t){e.$set(e.copyForm,"SITE",t)},expression:"copyForm.SITE"}},e._l(e.SelectSITEOptions,(function(e){return r("el-option",{key:e.id,attrs:{label:e.global_name,value:e.id}})})),1)],1),r("el-form-item",{attrs:{label:"段次",prop:"selectStage"}},[r("el-select",{staticStyle:{width:"150px"},attrs:{size:"mini",clearable:"",placeholder:"请选择"},on:{"visible-change":e.SelectStageDisplay},model:{value:e.copyForm.selectStage,callback:function(t){e.$set(e.copyForm,"selectStage",t)},expression:"copyForm.selectStage"}},e._l(e.SelectStageOptions,(function(e){return r("el-option",{key:e.id,attrs:{label:e.global_name,value:e.id}})})),1)],1),r("el-form-item",{attrs:{label:"胶料编号",prop:"selectRecipeNo"}},[r("el-select",{staticStyle:{width:"100px"},attrs:{filterable:"",size:"mini",clearable:"",placeholder:"请选择"},on:{"visible-change":e.SelectRecipeNoDisplay},model:{value:e.copyForm.selectRecipeNo,callback:function(t){e.$set(e.copyForm,"selectRecipeNo",t)},expression:"copyForm.selectRecipeNo"}},e._l(e.SelectRecipeNoOptions,(function(e){return r("el-option",{key:e.id,attrs:{label:e.product_no,value:e.id}})})),1)],1),r("el-form-item",{attrs:{label:"版本",prop:"version"}},[r("el-input",{staticStyle:{width:"90px"},attrs:{size:"mini",placeholder:"版本"},model:{value:e.copyForm.version,callback:function(t){e.$set(e.copyForm,"version",t)},expression:"copyForm.version"}})],1),r("el-form-item",{attrs:{label:"方案"}},[r("el-input",{staticStyle:{width:"90px"},attrs:{size:"mini",placeholder:"方案"},model:{value:e.copyForm.scheme,callback:function(t){e.$set(e.copyForm,"scheme",t)},expression:"copyForm.scheme"}})],1)],1),r("div",{staticClass:"dialog-footer",attrs:{slot:"footer"},slot:"footer"},[r("el-button",{attrs:{size:"mini"},on:{click:function(t){e.dialogCopyRecipeSync=!1}}},[e._v("取 消")]),r("el-button",{attrs:{size:"mini",type:"primary"},on:{click:function(t){return e.CopyRecipeConfirm("copyForm")}}},[e._v("确 定")])],1)],1)],1)},i=[],a=(r("96cf"),r("1da1")),c=r("5530"),l=r("3c17"),o=(r("a18c"),r("3eba"),r("2f62")),s={computed:Object(c["a"])({},Object(o["b"])(["permission"])),data:function(){return{loading:null,SelectEquipOptions:[],SelectCopyEquipOptions:[],SelectRecipeStatusOptions:[{value:1,label:"编辑"},{value:2,label:"提交"},{value:4,label:"启用"},{value:5,label:"驳回"},{value:6,label:"废弃"}],SelectSITEOptions:[],SelectSiteOptions:[],SelectStageOptions:[],SelectRecipeNoOptions:[],category__category_name:null,SelectEquip:null,SelectRecipeStatus:null,SelectSite:null,SelectStage:null,input_rubber_no:null,tableData:[],currentRow:{product_name:null,stage_name:null},currentPage:1,pageSize:10,tableDataTotal:0,dialogCopyRecipeSync:!1,copyForm:{CopySelectEquip:"",site:"",SITE:"",selectStage:"",selectRecipeNo:"",version:"",scheme:""},rules:{CopySelectEquip:[{required:!0,message:"请选择机台",trigger:"change"}],site:[{required:!0,message:"请选择产地",trigger:"change"}],SITE:[{required:!0,message:"请选择SITE",trigger:"change"}],selectStage:[{required:!0,message:"请选择段次",trigger:"change"}],selectRecipeNo:[{required:!0,message:"请选择胶料编号",trigger:"change"}],version:[{required:!0,message:"请填写版本",trigger:"change"}]}}},created:function(){this.permissionObj=this.permission,this.get_recipe_list(),this.site_list(),this.global_SITE_list(),this.stage_list(),this.recipe_no_list()},methods:{recipe_no_list:function(){var e=this;return Object(a["a"])(regeneratorRuntime.mark((function t(){var r;return regeneratorRuntime.wrap((function(t){while(1)switch(t.prev=t.next){case 0:return t.prev=0,t.next=3,Object(l["k"])("get",{params:{}});case 3:r=t.sent,0!==r.results.length&&(e.SelectRecipeNoOptions=r.results),t.next=10;break;case 7:throw t.prev=7,t.t0=t["catch"](0),new Error(t.t0);case 10:case"end":return t.stop()}}),t,null,[[0,7]])})))()},SelectRecipeNoDisplay:function(e){e&&this.recipe_no_list()},global_SITE_list:function(){var e=this;return Object(a["a"])(regeneratorRuntime.mark((function t(){var r;return regeneratorRuntime.wrap((function(t){while(1)switch(t.prev=t.next){case 0:return t.prev=0,t.next=3,Object(l["f"])("get",{params:{}});case 3:r=t.sent,0!==r.results.length&&(e.SelectSITEOptions=r.results),t.next=10;break;case 7:throw t.prev=7,t.t0=t["catch"](0),new Error(t.t0);case 10:case"end":return t.stop()}}),t,null,[[0,7]])})))()},SelectGlobalSITEDisplay:function(e){e&&this.global_SITE_list()},get_recipe_list:function(){var e=arguments,t=this;return Object(a["a"])(regeneratorRuntime.mark((function r(){var n,i,a,c,o,s,u;return regeneratorRuntime.wrap((function(r){while(1)switch(r.prev=r.next){case 0:return n=e.length>0&&void 0!==e[0]?e[0]:1,r.prev=1,i=t.SelectEquip?t.SelectEquip:"",a=t.SelectRecipeStatus?t.SelectRecipeStatus:"",c=t.SelectSite?t.SelectSite:"",o=t.SelectStage?t.SelectStage:"",s=t.input_rubber_no?t.input_rubber_no:"",t.loading=!0,r.next=10,Object(l["j"])("get",null,{params:{page:n,equip_id:i,used_type:a,factory_id:c,stage_id:o,stage_product_batch_no:s}});case 10:u=r.sent,t.tableData=u.results,t.tableDataTotal=u.count,t.loading=!1,t.currentRow={product_name:null,stage_name:null},r.next=21;break;case 17:throw r.prev=17,r.t0=r["catch"](1),t.loading=!1,new Error(r.t0);case 21:case"end":return r.stop()}}),r,null,[[1,17]])})))()},status_recipe_fun:function(e,t){var r=this;return Object(a["a"])(regeneratorRuntime.mark((function n(){return regeneratorRuntime.wrap((function(n){while(1)switch(n.prev=n.next){case 0:return n.prev=0,n.next=3,Object(l["j"])("patch",e,t);case 3:r.$message("状态切换成功"),r.get_recipe_list(r.currentPage),n.next=10;break;case 7:throw n.prev=7,n.t0=n["catch"](0),new Error(n.t0);case 10:case"end":return n.stop()}}),n,null,[[0,7]])})))()},delete_recipe_fun:function(e){return Object(a["a"])(regeneratorRuntime.mark((function t(){return regeneratorRuntime.wrap((function(t){while(1)switch(t.prev=t.next){case 0:return t.prev=0,t.next=3,Object(l["j"])("delete",e,{params:{}});case 3:t.next=8;break;case 5:throw t.prev=5,t.t0=t["catch"](0),new Error(t.t0);case 8:case"end":return t.stop()}}),t,null,[[0,5]])})))()},copy_recipe_list:function(e){return Object(a["a"])(regeneratorRuntime.mark((function t(){var r;return regeneratorRuntime.wrap((function(t){while(1)switch(t.prev=t.next){case 0:return t.prev=0,t.next=3,Object(l["i"])("post",null,e);case 3:return r=t.sent,t.abrupt("return",r);case 7:return t.prev=7,t.t0=t["catch"](0),t.abrupt("return",{error:t.t0});case 10:case"end":return t.stop()}}),t,null,[[0,7]])})))()},equip_list:function(){var e=this;return Object(a["a"])(regeneratorRuntime.mark((function t(){var r;return regeneratorRuntime.wrap((function(t){while(1)switch(t.prev=t.next){case 0:return t.prev=0,t.next=3,Object(l["e"])("get",{params:{category_name:"密炼设备"}});case 3:r=t.sent,0!==r.results.length&&(e.SelectEquipOptions=r.results),t.next=10;break;case 7:throw t.prev=7,t.t0=t["catch"](0),new Error(t.t0);case 10:case"end":return t.stop()}}),t,null,[[0,7]])})))()},equip_copy_list:function(e){var t=this;return Object(a["a"])(regeneratorRuntime.mark((function r(){var n;return regeneratorRuntime.wrap((function(r){while(1)switch(r.prev=r.next){case 0:return r.prev=0,r.next=3,Object(l["d"])("get",{params:{dev_type:e}});case 3:n=r.sent,t.SelectCopyEquipOptions=n.results,r.next=10;break;case 7:throw r.prev=7,r.t0=r["catch"](0),new Error(r.t0);case 10:case"end":return r.stop()}}),r,null,[[0,7]])})))()},site_list:function(){var e=this;return Object(a["a"])(regeneratorRuntime.mark((function t(){var r;return regeneratorRuntime.wrap((function(t){while(1)switch(t.prev=t.next){case 0:return t.prev=0,t.next=3,Object(l["m"])("get",{params:{}});case 3:r=t.sent,0!==r.results.length&&(e.SelectSiteOptions=r.results),t.next=10;break;case 7:throw t.prev=7,t.t0=t["catch"](0),new Error(t.t0);case 10:case"end":return t.stop()}}),t,null,[[0,7]])})))()},stage_list:function(){var e=this;return Object(a["a"])(regeneratorRuntime.mark((function t(){var r;return regeneratorRuntime.wrap((function(t){while(1)switch(t.prev=t.next){case 0:return t.prev=0,t.next=3,Object(l["n"])("get",{params:{}});case 3:r=t.sent,0!==r.results.length&&(e.SelectStageOptions=r.results),t.next=10;break;case 7:throw t.prev=7,t.t0=t["catch"](0),new Error(t.t0);case 10:case"end":return t.stop()}}),t,null,[[0,7]])})))()},SelectEquipDisplay:function(e){e&&this.equip_list()},SelectSiteDisplay:function(e){e&&this.site_list()},SelectStageDisplay:function(e){e&&this.stage_list()},SelectCopyEquipChange:function(){for(var e=0;e<this.SelectCopyEquipOptions.length;e++)this.copyForm.CopySelectEquip===this.SelectCopyEquipOptions[e]["id"]&&(this.category__category_name=this.SelectCopyEquipOptions[e]["category__category_name"])},handleCurrentChange:function(e){this.currentRow=e},pagehandleCurrentChange:function(e){this.currentRow=e,this.get_recipe_list(e),this.currentRow={product_name:null,stage_name:null}},usedTypeFormatter:function(e,t){return this.usedTypeChoice(e.used_type)},usedTypeChoice:function(e){switch(e){case 1:return"编辑";case 2:return"提交";case 3:return"校对";case 4:return"启用";case 5:return"驳回";case 6:return"废弃"}},RecipeSourceFormatter:function(e,t){return this.RecipeSourceChoice(e.batching_type)},RecipeSourceChoice:function(e){switch(e){case 1:return"上辅机";case 2:return"MES"}},status_true:function(){var e=Object(a["a"])(regeneratorRuntime.mark((function e(t){return regeneratorRuntime.wrap((function(e){while(1)switch(e.prev=e.next){case 0:return e.next=2,this.status_recipe_fun(t["id"],{data:{pass_flag:!0}});case 2:case"end":return e.stop()}}),e,this)})));function t(t){return e.apply(this,arguments)}return t}(),status_false:function(){var e=Object(a["a"])(regeneratorRuntime.mark((function e(t){return regeneratorRuntime.wrap((function(e){while(1)switch(e.prev=e.next){case 0:return e.next=2,this.status_recipe_fun(t["id"],{data:{pass_flag:!1}});case 2:case"end":return e.stop()}}),e,this)})));function t(t){return e.apply(this,arguments)}return t}(),SelectEquipChange:function(){this.get_recipe_list()},SelectRecipeStatusChange:function(){this.get_recipe_list()},SelectSiteChange:function(){this.get_recipe_list()},SelectStageChange:function(){this.get_recipe_list()},input_rubber_noChanged:function(){this.get_recipe_list()},recipe_display_change:function(e){this.$router.push({name:"RecipeDisplay",params:e}),this.$route.params},AddRecipeButton:function(){this.$router.push({name:"RecipeCreate",params:{}}),this.$route.params},ModifyRecipeButton:function(e){this.$router.push({name:"RecipeModify",params:e}),this.$route.params},handleRecipeDelete:function(e){var t=this;this.$confirm("此操作将永久删除"+e["stage_product_batch_no"]+", 是否继续?","提示",{confirmButtonText:"确定",cancelButtonText:"取消",type:"warning"}).then((function(){t.delete_recipe_fun(e["id"]),t.$message({type:"success",message:"删除成功!"}),t.get_recipe_list(t.currentPage)})).catch((function(){}))},CopyRecipeButton:function(){var e=Object(a["a"])(regeneratorRuntime.mark((function e(){return regeneratorRuntime.wrap((function(e){while(1)switch(e.prev=e.next){case 0:return this.$refs["copyForm"]&&this.$refs["copyForm"].resetFields(),this.copyForm.site=this.currentRow.factory_id,this.copyForm.SITE=this.currentRow.site_id,this.copyForm.selectStage=this.currentRow.stage_id,this.copyForm.selectRecipeNo=this.currentRow.product_info_id,this.copyForm.version=this.currentRow.versions,this.copyForm.scheme=this.currentRow.precept,this.dialogCopyRecipeSync=!0,e.next=10,this.equip_copy_list(this.currentRow["dev_type"]);case 10:case"end":return e.stop()}}),e,this)})));function t(){return e.apply(this,arguments)}return t}(),CopyRecipeConfirm:function(){var e=Object(a["a"])(regeneratorRuntime.mark((function e(t){var r=this;return regeneratorRuntime.wrap((function(e){while(1)switch(e.prev=e.next){case 0:this.$refs[t].validate((function(e){if(!e)return!1;Object(l["p"])({site:r.copyForm.SITE,product_info:r.copyForm.selectRecipeNo,versions:r.copyForm.version,equip:r.copyForm.CopySelectEquip,stage:r.copyForm.selectStage}).then((function(e){r.dialogCopyRecipeSync=!1;var t=Object.assign(r.currentRow,Object(c["a"])(Object(c["a"])({},r.copyForm),{},{copy_equip_id:r.copyForm.CopySelectEquip,category__category_name:r.category__category_name}));r.$router.push({name:"RecipeCopy",params:t}),r.$route.params})).catch((function(e){}))}));case 1:case"end":return e.stop()}}),e,this)})));function t(t){return e.apply(this,arguments)}return t}()}},u=s,p=r("2877"),m=Object(p["a"])(u,n,i,!1,null,"43958518",null);t["default"]=m.exports}}]);