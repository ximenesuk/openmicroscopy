//
// Copyright (C) 2013 University of Dundee & Open Microscopy Environment.
// All rights reserved.
//
// This program is free software: you can redistribute it and/or modify
// it under the terms of the GNU Affero General Public License as
// published by the Free Software Foundation, either version 3 of the
// License, or (at your option) any later version.
//
// This program is distributed in the hope that it will be useful,
// but WITHOUT ANY WARRANTY; without even the implied warranty of
// MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
// GNU Affero General Public License for more details.
//
// You should have received a copy of the GNU Affero General Public License
// along with this program.  If not, see <http://www.gnu.org/licenses/>.
//

/*global OME:true */
if (typeof OME === "undefined") {
    OME = {};
}

OME.multi_key = function() {
    if (navigator.appVersion.indexOf("Mac")!=-1) {
        return "meta";
    } else {
        return "ctrl";
    }
};

jQuery.fn.hide_if_empty = function() {
    if ($(this).children().length === 0) {
        $(this).hide();
    } else {
        $(this).show();
    }
  return this;
};

OME.addToBasket = function(selected, prefix) {
    var productListQuery = new Array("action=add");
    if (selected != null && selected.length > 0) {
        selected.each(function(i) {
            productListQuery[i+1]= $(this).attr('id').replace("-","=");
        });
    } else {
        OME.alert_dialog("Please select at least one element.");
        return;
    }
    $.ajax({
        type: "POST",
        url: prefix, //this.href,
        data: productListQuery.join("&"),
        success: function(responce){
            if(responce.match(/(Error: ([A-z]+))/gi)) {
                OME.alert_dialog(responce);
            } else {
                OME.calculateCartTotal(responce);
            }
        }
    });
};

// called from OME.tree_selection_changed() below
OME.handle_tree_selection = function(data) {
    var selected_objs = [];

    if (typeof data != 'undefined' && typeof data.inst != 'undefined') {
        
        var selected = data.inst.get_selected();
        var share_id = null;
        if (selected.length == 1) {
            var pr = selected.parent().parent();
            if (pr.length>0 && pr.attr('rel') && pr.attr('rel').replace("-locked", "")==="share") {
                share_id = pr.attr("id").split("-")[1];
            }
        }
        selected.each(function(){
            var $this = $(this),
                oid = $this.attr('id');
            if (typeof oid !== "undefined") {
                // after copy & paste, node will have id E.g. copy_dataset-123
                if (oid.substring(0,5) == "copy_") {
                    oid = oid.substring(5, oid.length);
                }
                var selected_obj = {"id":oid, "rel":$this.attr('rel')};
                selected_obj["class"] = $this.attr('class');
                if ($this.attr('data-fileset')) {
                    selected_obj["fileset"] = $this.attr('data-fileset');
                }
                if (share_id) {
                    selected_obj["share"] = share_id;
                }
                selected_objs.push(selected_obj);
            }
        });
    }
    $("body")
        .data("selected_objects.ome", selected_objs)
        .trigger("selection_change.ome");
};

// called on selection and deselection changes in jstree
OME.tree_selection_changed = function(data, evt) {
    // handle case of deselection immediately followed by selection - Only fire on selection
    if (typeof OME.select_timeout != 'undefined') {
        clearTimeout(OME.select_timeout);
    }
    OME.select_timeout = setTimeout(function() {
        OME.handle_tree_selection(data);
    }, 10);
};

// Short-cut to setting selection to [], with option to force refresh.
// (by default, center panel doesn't clear when nothing is selected)
OME.clear_selected = function(force_refresh) {
    var refresh = (force_refresh === true);
    $("body")
        .data("selected_objects.ome", [])
        .trigger("selection_change.ome", [refresh]);
};

// called when we change the index of a plate or acquisition
OME.field_selection_changed = function(field) {
    
    var datatree = $.jstree._focused();
    datatree.data.ui.last_selected;
    $("body")
        .data("selected_objects.ome", [{"id":datatree.data.ui.last_selected.attr("id"), "index":field}])
        .trigger("selection_change.ome", $(this).attr('id'));
};

// select all images from the specified fileset (if currently visible)
OME.select_fileset_images = function(filesetId) {
    var datatree = $.jstree._focused();
    $("#dataTree li[data-fileset="+filesetId+"]").each(function(){
        datatree.select_node(this);
    });
}

// actually called when share is edited, to refresh right-hand panel
OME.share_selection_changed = function(share_id) {
    $("body")
        .data("selected_objects.ome", [{"id": share_id}])
        .trigger("selection_change.ome");
};

// Standard ids are in the form TYPE-ID, web extensions may add an
// additional -SUFFIX
OME.table_selection_changed = function($selected) {
    var selected_objs = [];
    if (typeof $selected != 'undefined') {
        $selected.each(function(i){
            var id_split = this.id.split('-');
            var id_obj = id_split.slice(0, 2).join('-');
            var id_suffix = id_split.slice(2).join('-');
            selected_objs.push( {"id":id_obj, "id_suffix":id_suffix} );
        });
    }
    $("body")
        .data("selected_objects.ome", selected_objs)
        .trigger("selection_change.ome");
};

// handles selection for 'clicks' on table (search, history & basket)
// including multi-select for shift and meta keys
OME.handleTableClickSelection = function(event) {

    var $clickedRow = $(event.target).parents('tr:first');
    var rows = $("table#dataTable tbody tr");
    var selIndex = rows.index($clickedRow.get(0));
    
    if ( event.shiftKey ) {
        // get existing selected items
        var $s = $("table#dataTable tbody tr.ui-selected");
        if ($s.length === 0) {
            $clickedRow.addClass("ui-selected");
            OME.table_selection_changed($clickedRow);
            return;
        }
        var sel_start = rows.index($s.first());
        var sel_end = rows.index($s.last());
        
        // select all rows between new and existing selections
        var new_start, new_end;
        if (selIndex < sel_start) {
            new_start = selIndex;
            new_end = sel_start;
        } else if (selIndex > sel_end) {
            new_start = sel_end+1;
            new_end = selIndex+1;
        // or just from the first existing selection to new one
        } else {
            new_start = sel_start;
            new_end = selIndex;
        }
        for (var i=new_start; i<new_end; i++) {
            rows.eq(i).addClass("ui-selected");
        }
    }
    else if (event.metaKey) {
        if ($clickedRow.hasClass("ui-selected")) {
            $clickedRow.removeClass("ui-selected");
        }
        else {
            $clickedRow.addClass("ui-selected");
        }
    }
    else {
        rows.removeClass("ui-selected");
        $clickedRow.addClass("ui-selected");
    }
    // update right hand panel etc
    OME.table_selection_changed($("table#dataTable tbody tr.ui-selected"));
};

// called from click events on plate. Selected wells
OME.well_selection_changed = function($selected, well_index, plate_class) {
    var selected_objs = [];
    $selected.each(function(i){
        selected_objs.push( {"id":$(this).attr('id').replace("=","-"),
                "rel":$(this).attr('rel'),
                "index":well_index,
                "class":plate_class} );     // assume every well has same permissions as plate
    });
    
    $("body")
        .data("selected_objects.ome", selected_objs)
        .trigger("selection_change.ome");
};


// This is called by the Pagination controls at the bottom of icon or table pages.
// We simply update the 'page' data on the parent (E.g. dataset node in tree) and refresh
OME.doPagination = function(view, page) {
    var $container;
    if (view == "icon") {
        $container = $("#content_details");
    }
    else if (view == "table") {
        $container = $("#image_table");
    }
    var rel = $container.attr('rel').split("-");
    var $parent = $("#dataTree #"+ rel[0]+'-'+rel[1]);
    $parent.data("page", page);     // let the parent node keep track of current page
    $("#dataTree").jstree("refresh", $('#'+rel[0]+'-'+rel[1]));
    $parent.children("a:eq(0)").click();    // this will cause center and right panels to update
    return false;
}



// handle deleting of Tag, File, Comment
// on successful delete via AJAX, the parent .domClass is hidden
OME.removeItem = function(event, domClass, url, parentId, index) {
    var removeId = $(event.target).attr('id');
    var dType = removeId.split("-")[1]; // E.g. 461-comment
    // /webclient/action/remove/comment/461/?parent=image-257
    var $parent = $(event.target).parents(domClass);
    var $annContainer = $parent.parent();
    var confirm_remove = OME.confirm_dialog('Remove '+ dType + '?',
        function() {
            if(confirm_remove.data("clicked_button") == "OK") {
                $.ajax({
                    type: "POST",
                    url: url,
                    data: {'parent':parentId, 'index':index},
                    dataType: 'json',
                    success: function(r){
                        if(eval(r.bad)) {
                            OME.alert_dialog(r.errs);
                        } else {
                            // simply remove the item (parent class div)
                            //console.log("Success function");
                            $parent.remove();
                            $annContainer.hide_if_empty();
                        }
                    }
                });
            }
        }
    );
    return false;
};

OME.deleteItem = function(event, domClass, url) {
    var deleteId = $(event.target).attr('id');
    var dType = deleteId.split("-")[1]; // E.g. 461-comment
    // /webclient/action/delete/file/461/?parent=image-257
    var $parent = $(event.target).parents("."+domClass);
    var $annContainer = $parent.parent();
    var confirm_remove = OME.confirm_dialog('Delete '+ dType + '?',
        function() {
            if(confirm_remove.data("clicked_button") == "OK") {
                $.ajax({
                    type: "POST",
                    url: url,
                    dataType:'json',
                    success: function(r){
                        if(eval(r.bad)) {
                            OME.alert_dialog(r.errs);
                        } else {
                            // simply remove the item (parent class div)
                            $parent.remove();
                            $annContainer.hide_if_empty();
                            window.parent.OME.refreshActivities();
                        }
                    }
                });
            }
        }
    );
    event.preventDefault();
    return false;
};

// More code that is shared between metadata_general and batch_annotate panels
// Called when panel loaded. Does exactly what it says on the tin.
OME.initToolbarDropdowns = function() {
    // -- Toolbar buttons - show/hide dropdown options --
    $(".toolbar_dropdown ul").css('visibility', 'hidden');
    // show on click
    var $toolbar_dropdownlists = $(".toolbar_dropdown ul");
    $(".toolbar_dropdown button").click(function(e) {
        // hide any other lists that might be showing...
        $toolbar_dropdownlists.css('visibility', 'hidden');
        // then show this one...
        $("ul", $(this).parent()).css('visibility', 'visible');
        e.preventDefault();
        return false;
    });
    // on hover-out, hide drop-down menus
    $toolbar_dropdownlists.hover(function(){}, function(){
        $(this).css('visibility', 'hidden');
    });

    // For Figure scripts, we need a popup:
    $("#figScriptList li a").click(function(event){
        if (!$(this).parent().hasClass("disabled")) {
            OME.openScriptWindow(event, 800, 600);
        }
        event.preventDefault();
        return false;
    });
};

// Simply add query to thumbnail src to force refresh.
// By default we do ALL thumbnails, but can also specify ID
OME.refreshThumbnails = function(imageId) {
    var rdm = Math.random(),
        thumbs_selector = "#dataIcons img",
        spw_selector = "#spw img";
    // handle Dataset thumbs
    if (typeof imageId != "undefined") {
        thumbs_selector += "#"+imageId;
        spw_selector += "#image-"+imageId;
    }
    $(thumbs_selector).each(function(){
        var $this = $(this),
            base_src = $this.attr('src').split('?')[0];
        $this.attr('src', base_src + "?_="+rdm);
    });
    // handle SPW thumbs
    $(spw_selector).each(function(){
        var $this = $(this),
            base_src = $this.attr('src').split('?')[0];
        $this.attr('src', base_src + "?_="+rdm);
    });
    // Preview viewport
    $("#viewport-img").each(function(){
        var $this = $(this),
            base_src = $this.attr('src').split('?')[0];
        $this.attr('src', base_src + "?_="+rdm);
    });
}

jQuery.fn.tooltip_init = function() {
    $(this).tooltip({
        bodyHandler: function() {
                return $(this).parent().children("span.tooltip_html").html();
            },
        track: true,
        delay: 0,
        showURL: false,
        fixPNG: true,
        showBody: " - ",
        top: 10,
        left: -100
    });
  return this;
};
