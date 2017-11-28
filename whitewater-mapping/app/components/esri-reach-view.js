import Component from '@ember/component';
import Ember from 'ember';

export default Component.extend({

  classNames: ['scene-view'],

  esriLoader: Ember.inject.service('esri-loader'),

  mapDivId: 'esriView',

  // once we have a DOM node to attach the map to...
  didInsertElement() {

    this._super(...arguments);

    // load the esri modules
    this.get('esriLoader').loadModules(
      ['esri/views/MapView', 'esri/Map', 'esri/widgets/BasemapGallery', 'esri/widgets/LayerList']
    ).then(modules => {

      if (this.get('isDestroyed') || this.get('isDestroying')) {
        return;
      }

      const [MapView, Map, BasemapGallery, LayerList] = modules;

      // create a new map view
      this._view = new MapView({

        // An instance of Map
        map: new Map({
          basemap: 'dark-gray'
        }),

        // DOM div id
        container: this.mapDivId,

        // Meades Ranch, KS
        center: [-98.5422, 39.2241],
        zoom: 5

      });

      this._view.then(() => {

        // create some widgets
        this._basemapWidget = new BasemapGallery({
          view: this._view
        });
        this._layerlistWidget = new LayerList({
          view: this._view
        });

        // for right now, use the coordinates of Olympia as the zoomto location
        let X = -122.9007;
        let Y = 47.0379;
        this._view.goTo({
          center: [X, Y],
          zoom: 8,
          duration: 30000,
          easing: 'in-out-expo'
        });

        // TODO: move controls DOM into map div so fullscreen takes controls with it

      })
    });
  },

  _basemapWidgetVisible: false,
  _layerlistWidgetVisible: false,

  _removeBasemapWidget: function() {
    this._view.ui.remove(this._basemapWidget);
    this._basemapWidgetVisible = false;
  },
  _removeLayerlistWidget: function() {
    this._view.ui.remove(this._layerlistWidget);
    this._layerlistWidgetVisible = false;
  },

  actions: {

    toggleBasemap: function() {
      if (!this._basemapWidgetVisible) {
        this._removeLayerlistWidget();
        this._view.ui.add(this._basemapWidget, {
          position: 'top-right'
        });
        this._basemapWidgetVisible = true;
      } else {
        this._removeBasemapWidget();
      }
    },

    toggleLayerlist: function(){
      if (!this._layerlistWidgetVisible) {
        this._removeBasemapWidget();
        this._view.ui.add(this._layerlistWidget, {
          position: 'top-right'
        });
        this._layerlistWidgetVisible = true;
      } else {
        this._removeLayerlistWidget();
      }
    },

    mapFullscreen: function(){
      let elem = document.getElementById(this.mapDivId);
      if (elem.requestFullscreen) {
        elem.requestFullscreen();
      } else if (elem.msRequestFullscreen) {
        elem.msRequestFullscreen();
      } else if (elem.mozRequestFullScreen) {
        elem.mozRequestFullScreen();
      } else if (elem.webkitRequestFullscreen) {
        elem.webkitRequestFullscreen();
      }
      //TODO: add resize map to fill screen
    }

  },

  // destroy the map before this component is removed from the DOM
  willDestroyElement() {
    if (this._view) {
      delete this._view;
    }
  }
});
