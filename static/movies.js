// Kai psl uzsikrauna, pakvieciama si f-ja
$(document).ready(function() {
    $('#exampleModal').on('hide.bs.modal', function () {
        clearChildren($("#movie_list")[0]);
        location.reload();
    });
    $('#peopleModal').on('hide.bs.modal', function () {
        clearChildren($("#people_list")[0]);
    });
})


function clearChildren(parent) {
    while (parent.firstChild) {
        parent.removeChild(parent.firstChild);
    }
}


function displayMoviesByTitle(title) {
    jQuery.ajax({
        url: "/find_movies",
        type: "POST",
        dataType: "json",
        async: false,
        success: function (data) {
            console.log(data);
            list = document.getElementById("movie_list");
            for (var i = 0; i < data.length; i++) {
                var li = document.createElement("div");
                li.appendChild(createMovieDiv(data[i]));
                list.appendChild(li);
            }
        },
        data: JSON.stringify(title.value),
        contentType: 'application/json'
    })
    return false;
}


function createMovieDiv(movie) {
    var img = document.createElement("img");
    img.src = movie.poster;
    img.className = "poster";

    var p = document.createElement("p");
    p.textContent = movie.title + ", " + movie.year;

    var buttonWatchlist = document.createElement("button");
    buttonWatchlist.type = "button";
    buttonWatchlist.className = "btn btn-warning mr-1";
    if (movie.watch) {
        buttonWatchlist.disabled = true;
    }
    buttonWatchlist.onclick = function() { addToWatchlist(movie.id); buttonWatchlist.disabled = true; };
    buttonWatchlist.textContent = "+Watch";

    var buttonWishlist = document.createElement("button");
    buttonWishlist.type = "button";
    buttonWishlist.className = "btn btn-warning mr-1";
    if (movie.wish || movie.watch) {
        buttonWishlist.disabled = true;
    }
    buttonWishlist.onclick = function() { addToWishlist(movie.id); buttonWishlist.disabled = true; };
    buttonWishlist.textContent = "+Wish";

    var hr = document.createElement("hr");
    hr.className = "style8";

    var div = document.createElement("div");
    div.appendChild(img);
    div.appendChild(p);
    div.appendChild(buttonWatchlist);
    div.appendChild(buttonWishlist);
    div.appendChild(hr);

    return div;
}

function addToWatchlist(id) {
    jQuery.ajax({
        url: "/add_to_watchlist/" + id,
        type: "POST",
        async: false
    })
}


function addToWishlist(id) {
    jQuery.ajax({
        url: "/add_to_wishlist/" + id,
        type: "POST",
        async: false
    })
}

function addToFavourites(id) {
    jQuery.ajax({
        url: "/add_to_favourites/" + id,
        type: "POST",
        async: false
    })
}

function removeFromWatchlist(id) {
    jQuery.ajax({
        url: "/remove_from_watchlist/" + id,
        type: "POST",
        async: false
    })
}

function removeFromWishlist(id) {
    jQuery.ajax({
        url: "/remove_from_wishlist/" + id,
        type: "POST",
        async: false
    })
}

function removeFromFavourites(id) {
    jQuery.ajax({
        url: "/remove_from_favourites/" + id,
        type: "POST",
        async: false
    })
}

function transferToWatchlist(id) {
    jQuery.ajax({
        url: "/transfer_to_watchlist/" + id,
        type: "POST",
        async: false
    })
}

var movieIdForReview = 0;

function postReview(review, rating) {
    jQuery.ajax({
        url: "/post_review/" + movieIdForReview,
        type: "POST",
        dataType: "json",
        async: false,
        data: JSON.stringify({reviewText: review.value, rating: rating.value}),
        contentType: 'application/json'
    })
    $('#reviewModal').modal('hide');
    return false;
}

function displayPeople(name, surname) {
    jQuery.ajax({
        url: "/find_people",
        type: "POST",
        dataType: "json",
        async: false,
        success: function (data) {
            console.log(data);
            list = document.getElementById("people_list");
            for (var i = 0; i < data.length; i++) {
                var li = document.createElement("div");
                li.appendChild(createPersonDiv(data[i]));
                list.appendChild(li);
            }
        },
        data: JSON.stringify({name: name.value, surname: surname.value}),
        contentType: 'application/json'
    })
    return false;
}

function createPersonDiv(person) {
    var img = document.createElement("img");
    if (person.img_data === null) {
        img.src = "/static/pics/default.png";
    }
    else {
        img.src = person.img_data;
    }
    img.className = "person_pic";

    var p = document.createElement("p");
    p.textContent = person.name + " " + person.surname;

    var buttonAdd = document.createElement("button");
    buttonAdd.type = "button";
    buttonAdd.className = "btn btn-warning mr-1";
    if (person.friend) {
        buttonAdd.disabled = true;
    }
    buttonAdd.onclick = function() { addToFriends(person.id); buttonAdd.disabled = true; };
    buttonAdd.textContent = "Add friend";

    var hr = document.createElement("hr");
    hr.className = "style8";

    var div = document.createElement("div");
    div.appendChild(img);
    div.appendChild(p);
    div.appendChild(buttonAdd);
    div.appendChild(hr);

    return div;
}

function addToFriends(id) {
    jQuery.ajax({
        url: "/add_to_friends/" + id,
        type: "POST",
        async: false
    })
}

function redHeartClick(btn, movieId) {
    if ($("#red-heart" + movieId).css('display') == 'none') {
        return;
    }
    $("#red-heart" + movieId).toggleClass("d-none");
    $("#black-heart" + movieId).toggleClass("d-none");
    removeFromFavourites(movieId)
}

function blackHeartClick(btn, movieId) {
    if ($("#black-heart" + movieId).css('display') == 'none') {
        return;
    }
    $("#black-heart" + movieId).toggleClass("d-none");
    $("#red-heart" + movieId).toggleClass("d-none");
    addToFavourites(movieId)
}

function markAsUseful(id) {
    jQuery.ajax({
        url: "/mark_as_useful/" + id,
        type: "POST",
        async: false
    })
}

