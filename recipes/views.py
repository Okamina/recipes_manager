#!/usr/bin/env python
# encoding: utf-8
from flask import request, redirect, flash, url_for, render_template
from main import app, db
from models import Recipe
from flask_login import current_user,  login_required
from forms import RecipeForm

@app.route('/all_recipes', methods=['GET'])
def all_recipes():
    recipes = Recipe.query.filter_by(is_public=True).order_by(Recipe.id.desc()).all()
    return render_template('recipes/all_recipes.html', recipes=recipes)

@app.route('/my_recipes', methods=['GET'])
@login_required
def my_recipes():
    recipes = Recipe.query.filter_by(user=current_user).order_by(Recipe.id.desc()).all()
    return render_template('recipes/my_recipes.html', recipes=recipes)

@app.route('/new_recipe', methods=['GET', 'POST'])
@login_required
def new_recipe():
    form = RecipeForm(request.form)
    if request.method == 'GET':
        return render_template('recipes/new.html', form=form)
    if form.validate():
        # https://stackoverflow.com/questions/33429510/wtforms-selectfield-not-properly-coercing-for-booleans fuck
        if form.is_public.data == '':
            form.is_public.data = False
        recipe = Recipe(
            title=form.title.data,
            ingredients=form.ingredients.data,
            time_needed=form.time_needed.data,
            steps=form.steps.data,
            is_public=form.is_public.data,
            user_id=current_user.id)
        db.session.add(recipe)
        db.session.commit()
        flash('Recipe added successfully', 'success')
        return redirect(url_for('show_recipe', recipe_id=recipe.id))

    flash('There are some problems here', 'danger')
    return render_template('recipes/new.html', form=form)

@app.route('/recipe/<recipe_id>', methods=['GET'])
def show_recipe(recipe_id):
    # TODO: check if the user can view this particular recipe -
    # is public or recipe.user_id=current_user.id
    recipe = Recipe.query.get(recipe_id)
    return render_template('recipes/show.html', recipe=recipe)

@app.route('/recipe/<recipe_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_recipe(recipe_id):
    form = RecipeForm(request.form)
    recipe = Recipe.query.filter_by(id=recipe_id).first_or_404()
    if request.method == 'POST':
        recipe.title = form.title.data
        recipe.ingredients = form.ingredients.data
        recipe.time_needed = form.time_needed.data
        recipe.steps = form.steps.data
        recipe.is_public = bool(form.is_public.data)
        db.session.commit()
        flash('Recipe edited successfully', 'success')
        return redirect(url_for('my_recipes'))
    # This below is because of boolean vs string conversion. By default, values for radio buttons are strings.
    # If recipe was private, it was '' converted to boolean, but False cannot be converted to ''.
    if recipe.is_public == False:
        form.is_public.default = ''
        form.process()
    # I need to set the values for ingredients and steps, because they're from textarea, and that
    # doesn't support value for field.
    form.ingredients.data = recipe.ingredients
    form.steps.data = recipe.steps
    return render_template('recipes/edit.html', form=form, recipe=recipe)

@app.route('/recipe/<recipe_id>/delete', methods=['GET', 'POST'])
@login_required
def delete_recipe(recipe_id):
    # TODO: add a check for recipe.user_id = current_user.id
    recipe = Recipe.query.filter_by(id=recipe_id).first_or_404()
    db.session.delete(recipe)
    db.session.commit()
    flash('Deleted post successfully', 'success')
    return redirect(url_for('my_recipes'))
