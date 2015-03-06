from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from rango.models import Category
from rango.models import Page
from rango.forms import CategoryForm
from rango.forms import PageForm
from rango.forms import UserForm, UserProfileForm
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from datetime import datetime
from rango.bing_search import run_query


@login_required
def restricted(request):
    context_dict = {'boldmessage': ""}
    return render(request, 'rango/restricted.html', context_dict)

# Use the login_required() decorator to ensure only those logged in can access the view.
@login_required


def add_page(request, category_name_slug):

    try:
        cat = Category.objects.get(slug=category_name_slug)
    except Category.DoesNotExist:
                cat = None

    if request.method == 'POST':
        form = PageForm(request.POST)
        if form.is_valid():
            if cat:
                page = form.save(commit=False)
                page.category = cat
                page.views = 0
                page.save()
                # probably better to use a redirect here.
                return category(request, category_name_slug)
        else:
            print form.errors
    else:
        form = PageForm()

    context_dict = {'form':form, 'category': cat, 'category_name_slug': category_name_slug}

    return render(request, 'rango/add_page.html', context_dict)
	
	

def add_category(request):
    # A HTTP POST?
    if request.method == 'POST':
        form = CategoryForm(request.POST)

        # Have we been provided with a valid form?
        if form.is_valid():
            # Save the new category to the database.
            form.save(commit=True)

            # Now call the index() view.
            # The user will be shown the homepage.
            return index(request)
        else:
            # The supplied form contained errors - just print them to the terminal.
            print form.errors
    else:
        # If the request was not a POST, display the form to enter details.
        form = CategoryForm()

    # Bad form (or form details), no form supplied...
    # Render the form with error messages (if any).
    return render(request, 'rango/add_category.html', {'form': form})
	
	

def category(request, category_name_slug):

    # Create a context dictionary which we can pass to the template rendering engine.
    context_dict = {}
    try:
        # Can we find a category name slug with the given name?
        # If we can't, the .get() method raises a DoesNotExist exception.
        # So the .get() method returns one model instance or raises an exception.
		category = Category.objects.get(slug=category_name_slug)
		context_dict['category_name'] = category.name
		context_dict['category_name_slug'] = category_name_slug

        # Retrieve all of the associated pages.
        # Note that filter returns >= 1 model instance.
		pages = Page.objects.filter(category=category)

        # Adds our results list to the template context under name pages.
		context_dict['pages'] = pages
        # We also add the category object from the database to the context dictionary.
        # We'll use this in the template to verify that the category exists.
		context_dict['category'] = category
    except Category.DoesNotExist:
        # We get here if we didn't find the specified category.
        # Don't do anything - the template displays the "no category" message for us.
        pass
	

    if request.method == 'POST':
        query = request.POST.get('query')
        if query:
			query = query.strip()
            # Run our Bing function to get the results list!
     			result_list = run_query(query)
			context_dict['result_list'] = result_list
    # Go render the response and return it to the client.
    return render(request, 'rango/category.html', context_dict)


def index(request):

    category_list = Category.objects.order_by('-likes')[:5]
    page_list = Page.objects.order_by('-views')[:5]

    context_dict = {'categories': category_list, 'pages': page_list}

    visits = request.session.get('visits')
    if not visits:
        visits = 1
    reset_last_visit_time = False

    last_visit = request.session.get('last_visit')
    if last_visit:
        last_visit_time = datetime.strptime(last_visit[:-7], "%Y-%m-%d %H:%M:%S")

        if (datetime.now() - last_visit_time).seconds > 0:
            # ...reassign the value of the cookie to +1 of what it was before...
            visits = visits + 1
            # ...and update the last visit cookie, too.
            reset_last_visit_time = True
    else:
        # Cookie last_visit doesn't exist, so create it to the current date/time.
        reset_last_visit_time = True

    if reset_last_visit_time:
        request.session['last_visit'] = str(datetime.now())
        request.session['visits'] = visits
    context_dict['visits'] = visits


    response = render(request,'rango/index.html', context_dict)

    return response
	
	
def about(request):
    # Construct a dictionary to pass to the template engine as its context.
    # Note the key boldmessage is the same as {{ boldmessage }} in the template!
    context_dict = {'boldmessage': ""}
	# If the visits session varible exists, take it and use it.
	# If it doesn't, we haven't visited the site so set the count to zero.
    if request.session.get('visits'):
		count = request.session.get('visits')
    else:
		count = 0
    # Return a rendered response to send to the client.
    # We make use of the shortcut function to make our lives easier.
    # Note that the first parameter is the template we wish to use.

    return render(request, 'rango/about.html', {'visits':count})
   
def search(request):

    result_list = []

    if request.method == 'POST':
        query = request.POST['query'].strip()

        if query:
            # Run our Bing function to get the results list!
            result_list = run_query(query)

    return render(request, 'rango/search.html', {'result_list': result_list})
	
def track_url():
	context = RequestContext(request) 
	page_id = None 
	url = '/rango/' 
	if request.method == 'GET': 
		if 'page_id' in request.GET:
			page_id = request.GET['page_id']
			try: 
				page = Page.objects.get(id=page_id) 
				page.views = page.views + 1 
				page.save() 
				url = page.url 
			except: 
				pass 
				
	return redirect(url)
	
from rango.forms import UserForm, UserProfileForm

	
def register_profile(request):
	# Request the context.
	#context = RequestContext(request)
	#cat_list = get_category_list()
	context_dict = {}
	#context_dict['cat_list'] = cat_list
	#	Boolean telling us whether registration was successful or not.
	# Initially False; presume it was a failure until proven otherwise!
	registered = False
	# If HTTP POST, we wish to process form data and create an account.
	if request.method == 'POST':
		# Grab raw form data - making use of both FormModels.
		user_form = UserForm(data=request.POST)
		profile_form = UserProfileForm(data=request.POST)
		# Two valid forms?
		if user_form.is_valid() and profile_form.is_valid():
			# Save the user's form data. That one is easy.
			user = user_form.save()
			# Now a user account exists, we hash the password with the set_password() method.
			# Then we can update the account with .save().
			user.set_password(user.password)
			user.save()
			# Now we can sort out the UserProfile instance.
			# We'll be setting values for the instance ourselves, so commit=False prevents Django from saving the instance automatically.
			profile = profile_form.save(commit=False)
			profile.user = user
			# Profile picture supplied? If so, we put it in the new UserProfile.
			if 'picture' in request.FILES:
				profile.picture = request.FILES['picture']
				# Now we save the model instance!
				profile.save()
				# We can say registration was successful.
				registered = True
				# Invalid form(s) - just print errors to the terminal.
		else:
			print user_form.errors, profile_form.errors
			# Not a HTTP POST, so we render the two ModelForms to allow a user to input their data.
	else:
		user_form = UserForm()
		profile_form = UserProfileForm()
			
	context_dict['user_form'] = user_form
	context_dict['profile_form']= profile_form
	context_dict['registered'] = registered
			
			# Render and return!
	return render(request,
		'rango/profile_registration.html',
		context_dict)
		
def profile(request):
	#context = RequestContext(request)
	#cat_list = get_category_list()
	#context_dict = {'cat_list': cat_list}
	#profile_form = UserProfileForm(data=request.POST)
	#user = profile_form.save()
	
	context_dict = {}
	#u = user.objects.get(username=request.user)
	try:
		up = UserProfile.objects.get(user=u)
	except:
		up = None
	#context_dict['user'] = u
	context_dict['userprofile'] = up
	return render(request, 'rango/profile.html', context_dict)