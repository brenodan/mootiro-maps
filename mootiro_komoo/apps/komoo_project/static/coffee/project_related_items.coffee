define ['lib/underscore-min', 'lib/backbone-min'], () ->
    $ = jQuery

    window.PartnersLogo = Backbone.Model.extend
        toJSON: (attr) ->
            Backbone.Model.prototype.toJSON.call this, attr

    window.PartnersLogoView = Backbone.View.extend
        className: 'partner-logo'
        tagName: 'li'

        initialize: () ->
            _.bindAll this, 'render'
            @template = _.template """
                <a href="<%= url %>">
                    <img src="<%= url %>" class="ad_image_gallery_thumb" />
                </a>
            """

        render: () ->
            console.log 'rendering model: ', @model.toJSON()
            renderedContent = @template @model.toJSON()
            $(@el).html renderedContent
            this

    window.PartnersLogos = Backbone.Collection.extend
        model: PartnersLogo

    window.PartnersLogosView = Backbone.View.extend
        initialize: () ->
            _.bindAll this, 'render'
            @template = _.template """
                <div class="proj-partners-title">Parceiros:</div>
                <div id="logos-gallery" class="ad-gallery">
                    <div class="ad-image-wrapper"></div>
                    <div class="ad-controls"></div>
                    <div class="ad-nav">
                        <div class="ad-thumbs">
                            <ul class="ad-thumb-list"></ul>
                        </div>
                    </div>
                </div>
            """
            @collection.bind 'reset', @render

        render: () ->
            collection = @collection
            @$el.html @template()
            $logos = this.$ '.ad-thumb-list'
            $gallery = this.$ '#logos-gallery'

            collection.each (logo) ->
                console.log '-----', logo
                view = new PartnersLogoView
                    model: logo
                $logos.append view.render().$el

            $gallery.adGallery
                width: 250
                height:150
                update_window_hash: no
                slideshow:
                    enable: true
                    autostart: true
                    speed: 3500

            this

    $ ->
        KomooNS.drawFeaturesList()

        panelInfoView = new PanelInfoView
            model: new PanelInfo KomooNS.obj
        $('.panel-info-wrapper').append panelInfoView.render().$el

        partnersLogosView = new PartnersLogosView
            collection: new PartnersLogos().reset KomooNS.obj.partners_logo
        $('.panel-info-wrapper').append partnersLogosView.render().$el

