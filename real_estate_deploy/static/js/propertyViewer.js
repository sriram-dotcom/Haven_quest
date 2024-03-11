function PropertyViewer(myBookings, numRows, propertiesPerRow) {
    const PROPERTIES_PER_PAGE = numRows * propertiesPerRow;

    this.updateCards = (properties) => {
        // properties: [{bookedOrOwned: -1}, {bookedOrOwned: 2}, {}]
        $('#cards').empty();

        for (let row = 0; row < numRows; row++) {
            const deck = $('<div class="card-deck"></div>');

            for (let col = 0; col < propertiesPerRow; col++) {
                const index = row * propertiesPerRow + col;
                if (index < properties.length) {
                    const property = properties[row * propertiesPerRow + col];
                    // let type = '';

                    // if (property.bookedOrOwned == -1){
                    //     type = 'booked';
                    // }
                    // else if (property.bookedOrOwned == 2){
                    //     type = 'owned';
                    // }

                    const card = $(`
                        <div class="card ${myBookings != null && myBookings ? '' : property.type}">
                            <img class="card-img-top" src="/static/img/real_estate/${property.image}">
                            <div class="card-body">
                                <h5 class="card-title">${property.name}</h5>
                                <p class="card-text">${property.description}</p>
                                <p class="card-price">$${property.price}</p>
                                <p class="card-text">${property.address}</p>
                                <p class="card-text">${property.country}</p>
                                <button class="book-button btn btn-primary">
                                    ${myBookings == null ? 'Remove Property' : myBookings ? 'Cancel Booking' : 'Book Visit'}
                                </button>
                            </div>
                        </div>
                    `);
                    console.log("it gets here");
                    $(card).find('.book-button').on('click', _ => {
                        if (myBookings == null)
                            this.removeProperty(property);
                        else if (myBookings)
                            this.cancelBooking(property);
                        else
                            this.bookVisit(property);
                    });

                    $(deck).append(card);
                } else {
                    // Add empty cards for alignment if necessary
                    $(deck).append('<div class="card invisible"></div>');
                }
            }

            $('#cards').append(deck);
        }
    };

    const createPageLink = (text, toPage, active, disabled) => {
        const link = $(`
            <li class="page-item">
                <a class="page-link">${text}</a>
            </li>
        `);
        $(link).find('.page-link').on('click', _ => {
            this.currentPage = toPage;
            this.load();
        });
        if (active)
            link.addClass('active');
        if (disabled)
            link.addClass('disabled');
        return link;
    };

    this.currentPage = 1;

    this.updatePagination = (total) => {
        let pages = Math.ceil(total / PROPERTIES_PER_PAGE);
        $('#paginator').empty().append(
            createPageLink('Previous', this.currentPage - 1, false, this.currentPage == 1)
        );
        for (let page = 1; page <= pages; page++)
            $('#paginator').append(
                createPageLink(page, page, page == this.currentPage, false)
            );
        $('#paginator').append(
            createPageLink('Next', this.currentPage + 1, false, this.currentPage == pages)
        );
    };

    this.update = (data) => {
        this.updateCards(data.properties);
        this.updatePagination(data.total);
    };

    this.load = () => {
        console.log("myBookings: " + myBookings);
        $.get(myBookings == null ? '/api/my_properties' : myBookings ? '/api/my_bookings' : '/api/get_properties', {
            n: PROPERTIES_PER_PAGE,
            offset: (this.currentPage - 1) * PROPERTIES_PER_PAGE
        }, (data) => {
            // this.addPropertiesType(data);
            this.update(data);
        });
    };

    this.addPropertiesType = (data) => {
        if (myBookings) {

        }
        else {
            // Make all properties have an empty type
            // so they can be shown to everyone
            for (let i=0; i<data.properties.length; i++) {
                data.properties[i].type = '';
            }
        }
    };

    this.bookVisit = (property) => {
        $.post('/api/book_visit', {
            property_id: property.id,
            n: PROPERTIES_PER_PAGE,
            offset: (this.currentPage - 1) * PROPERTIES_PER_PAGE
        }, (data) => {
            this.update(data);
        }).fail(function(response) {
            location.href = "login"
        });
    };

    this.cancelBooking = (property) => {
        $.post('/api/cancel_booking', {
            property_id: property.id,
            n: PROPERTIES_PER_PAGE,
            offset: (this.currentPage - 1) * PROPERTIES_PER_PAGE
        }, (data) => {
            this.update(data);
        });
    };

    this.removeProperty = (property) => {
        $.post('/api/remove_property', {
            property_id: property.id,
            n: PROPERTIES_PER_PAGE,
            offset: (this.currentPage - 1) * PROPERTIES_PER_PAGE
        }, (data) => {
            this.update(data);
        });
    };
}
