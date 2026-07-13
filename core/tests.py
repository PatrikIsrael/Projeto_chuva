from datetime import date, timedelta
from django.test import TestCase, Client
from django.urls import reverse, resolve
from django.contrib.auth.models import User
from django.contrib.messages import get_messages
from .models import RegistroChuva, UserProfile
from .forms import RegistroChuvaForm, SomarPeriodoForm, SignupForm, PerfilForm
from . import views


class RegistroChuvaModelTest(TestCase):
    def setUp(self):
        self.usuario = User.objects.create_user(username='testuser', password='12345')
        self.registro = RegistroChuva.objects.create(
            usuario=self.usuario,
            data=date.today(),
            milimetros=25.5,
            observacao='Chuva forte',
        )

    def test_criar_registro(self):
        self.assertEqual(RegistroChuva.objects.count(), 1)
        self.assertEqual(self.registro.usuario, self.usuario)
        self.assertEqual(self.registro.milimetros, 25.5)
        self.assertEqual(self.registro.observacao, 'Chuva forte')

    def test_string_representation(self):
        expected = f'{self.usuario.username} - {date.today()}: 25.5 mm'
        self.assertEqual(str(self.registro), expected)

    def test_unique_together_usuario_data(self):
        with self.assertRaises(Exception):
            RegistroChuva.objects.create(
                usuario=self.usuario,
                data=date.today(),
                milimetros=10.0,
            )

    def test_ordering_descendente(self):
        data_ontem = date.today() - timedelta(days=1)
        registro2 = RegistroChuva.objects.create(
            usuario=self.usuario,
            data=data_ontem,
            milimetros=5.0,
        )
        registros = list(RegistroChuva.objects.all())
        self.assertEqual(registros[0], self.registro)
        self.assertEqual(registros[1], registro2)

    def test_observacao_opcional(self):
        registro = RegistroChuva.objects.create(
            usuario=self.usuario,
            data=date.today() + timedelta(days=1),
            milimetros=10.0,
        )
        self.assertIsNone(registro.observacao)

    def test_milimetros_valor_inteiro(self):
        registro = RegistroChuva.objects.create(
            usuario=self.usuario,
            data=date.today() + timedelta(days=2),
            milimetros=10,
        )
        self.assertEqual(registro.milimetros, 10)


class RegistroChuvaFormTest(TestCase):
    def test_form_valido(self):
        form_data = {
            'data': date.today(),
            'milimetros': 15.5,
            'observacao': 'Chuva moderada',
        }
        form = RegistroChuvaForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_form_valido_sem_observacao(self):
        form_data = {
            'data': date.today(),
            'milimetros': 10.0,
        }
        form = RegistroChuvaForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_milimetros_negativo_invalido(self):
        form_data = {
            'data': date.today(),
            'milimetros': -5.0,
        }
        form = RegistroChuvaForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('milimetros', form.errors)

    def test_milimetros_muito_alto_invalido(self):
        form_data = {
            'data': date.today(),
            'milimetros': 1000.0,
        }
        form = RegistroChuvaForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('milimetros', form.errors)

    def test_data_futura_invalida(self):
        form_data = {
            'data': date.today() + timedelta(days=5),
            'milimetros': 10.0,
        }
        form = RegistroChuvaForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('data', form.errors)

    def test_milimetros_zero_valido(self):
        form_data = {
            'data': date.today(),
            'milimetros': 0.0,
        }
        form = RegistroChuvaForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_milimetros_proximo_maximo_valido(self):
        form_data = {
            'data': date.today(),
            'milimetros': 999.8,
        }
        form = RegistroChuvaForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_campos_required(self):
        form = RegistroChuvaForm(data={})
        self.assertFalse(form.is_valid())
        self.assertIn('data', form.errors)
        self.assertIn('milimetros', form.errors)


class SomarPeriodoFormTest(TestCase):
    def test_form_valido(self):
        form_data = {
            'inicio': date.today() - timedelta(days=7),
            'fim': date.today(),
        }
        form = SomarPeriodoForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_inicio_depois_fim_invalido(self):
        form_data = {
            'inicio': date.today(),
            'fim': date.today() - timedelta(days=7),
        }
        form = SomarPeriodoForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('__all__', form.errors)

    def test_inicio_igual_fim_valido(self):
        form_data = {
            'inicio': date.today(),
            'fim': date.today(),
        }
        form = SomarPeriodoForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_campos_required(self):
        form = SomarPeriodoForm(data={})
        self.assertFalse(form.is_valid())
        self.assertIn('inicio', form.errors)
        self.assertIn('fim', form.errors)


class HomeViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.usuario = User.objects.create_user(
            username='testuser', password='12345'
        )
        RegistroChuva.objects.create(
            usuario=self.usuario,
            data=date.today(),
            milimetros=30.0,
        )

    def test_redireciona_se_nao_autenticado(self):
        response = self.client.get(reverse('core:home'))
        self.assertEqual(response.status_code, 302)
        self.assertIn('/login/', response.url)

    def test_status_code_autenticado(self):
        self.client.login(username='testuser', password='12345')
        response = self.client.get(reverse('core:home'))
        self.assertEqual(response.status_code, 200)

    def test_template_usado(self):
        self.client.login(username='testuser', password='12345')
        response = self.client.get(reverse('core:home'))
        self.assertTemplateUsed(response, 'core/home.html')

    def test_context_contem_form(self):
        self.client.login(username='testuser', password='12345')
        response = self.client.get(reverse('core:home'))
        self.assertIn('form', response.context)
        self.assertIn('form_soma', response.context)

    def test_context_contem_ultimos_registros(self):
        self.client.login(username='testuser', password='12345')
        response = self.client.get(reverse('core:home'))
        self.assertIn('ultimos_registros', response.context)
        self.assertEqual(len(response.context['ultimos_registros']), 1)

    def test_post_cria_registro(self):
        self.client.login(username='testuser', password='12345')
        yesterday = date.today() - timedelta(days=1)
        response = self.client.post(reverse('core:home'), {
            'salvar_chuva': '1',
            'data': yesterday,
            'milimetros': 12.5,
            'observacao': 'Teste',
        })
        self.assertEqual(response.status_code, 302)
        self.assertEqual(RegistroChuva.objects.count(), 2)
        registro = RegistroChuva.objects.get(usuario=self.usuario, data=yesterday)
        self.assertEqual(registro.milimetros, 12.5)

    def test_post_atualiza_registro_existente(self):
        self.client.login(username='testuser', password='12345')
        response = self.client.post(reverse('core:home'), {
            'salvar_chuva': '1',
            'data': date.today(),
            'milimetros': 50.0,
            'observacao': 'Atualizado',
        })
        self.assertEqual(response.status_code, 302)
        registro = RegistroChuva.objects.get(usuario=self.usuario, data=date.today())
        self.assertEqual(registro.milimetros, 50.0)
        self.assertEqual(RegistroChuva.objects.count(), 1)

    def test_post_com_form_invalido(self):
        self.client.login(username='testuser', password='12345')
        response = self.client.post(reverse('core:home'), {
            'salvar_chuva': '1',
            'data': '',
            'milimetros': '',
        })
        self.assertEqual(response.status_code, 200)
        self.assertIn('form', response.context)

    def test_soma_periodo_no_context(self):
        self.client.login(username='testuser', password='12345')
        RegistroChuva.objects.create(
            usuario=self.usuario,
            data=date.today() - timedelta(days=1),
            milimetros=20.0,
        )
        response = self.client.get(reverse('core:home'), {
            'inicio': date.today() - timedelta(days=7),
            'fim': date.today(),
        })
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['total_periodo'], 50.0)
        self.assertEqual(len(response.context['registros_periodo']), 2)

    def test_mensagem_sucesso_criacao(self):
        self.client.login(username='testuser', password='12345')
        yesterday = date.today() - timedelta(days=1)
        response = self.client.post(reverse('core:home'), {
            'salvar_chuva': '1',
            'data': yesterday,
            'milimetros': 5.0,
        }, follow=True)
        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(any('criado' in str(m) for m in messages))

    def test_mensagem_sucesso_atualizacao(self):
        self.client.login(username='testuser', password='12345')
        response = self.client.post(reverse('core:home'), {
            'salvar_chuva': '1',
            'data': date.today(),
            'milimetros': 40.0,
        }, follow=True)
        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(any('atualizado' in str(m) for m in messages))


class ExcluirRegistroViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.usuario = User.objects.create_user(
            username='testuser', password='12345'
        )
        self.outro_usuario = User.objects.create_user(
            username='outro', password='12345'
        )
        self.registro = RegistroChuva.objects.create(
            usuario=self.usuario,
            data=date.today(),
            milimetros=15.0,
        )

    def test_redireciona_se_nao_autenticado(self):
        response = self.client.post(
            reverse('core:excluir_registro', args=[self.registro.id])
        )
        self.assertEqual(response.status_code, 302)
        self.assertIn('/login/', response.url)

    def test_exclusao_com_post(self):
        self.client.login(username='testuser', password='12345')
        response = self.client.post(
            reverse('core:excluir_registro', args=[self.registro.id])
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(RegistroChuva.objects.count(), 0)

    def test_nao_exclui_com_get(self):
        self.client.login(username='testuser', password='12345')
        response = self.client.get(
            reverse('core:excluir_registro', args=[self.registro.id])
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(RegistroChuva.objects.count(), 1)

    def test_apenas_dono_pode_excluir(self):
        self.client.login(username='outro', password='12345')
        response = self.client.post(
            reverse('core:excluir_registro', args=[self.registro.id])
        )
        self.assertEqual(response.status_code, 404)
        self.assertEqual(RegistroChuva.objects.count(), 1)

    def test_mensagem_sucesso_exclusao(self):
        self.client.login(username='testuser', password='12345')
        response = self.client.post(
            reverse('core:excluir_registro', args=[self.registro.id]),
            follow=True,
        )
        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(any('excluído' in str(m) for m in messages))

    def test_404_se_registro_inexistente(self):
        self.client.login(username='testuser', password='12345')
        response = self.client.post(
            reverse('core:excluir_registro', args=[99999])
        )
        self.assertEqual(response.status_code, 404)


class SignupViewTest(TestCase):
    def setUp(self):
        self.client = Client()

    def test_template_usado(self):
        response = self.client.get(reverse('core:signup'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'registration/signup.html')

    def test_signup_cria_usuario(self):
        response = self.client.post(reverse('core:signup'), {
            'username': 'novouser',
            'password1': 'teste@123#Seguro',
            'password2': 'teste@123#Seguro',
        })
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('login'))
        self.assertEqual(User.objects.count(), 1)

    def test_signup_senhas_diferentes(self):
        response = self.client.post(reverse('core:signup'), {
            'username': 'novouser',
            'password1': 'senha123',
            'password2': 'senha456',
        })
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.context['form'].is_valid())

    def test_signup_usuario_existente(self):
        User.objects.create_user(username='existente', password='12345')
        response = self.client.post(reverse('core:signup'), {
            'username': 'existente',
            'password1': 'teste@123#Seguro',
            'password2': 'teste@123#Seguro',
        })
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.context['form'].is_valid())

    def test_mensagem_sucesso_signup(self):
        response = self.client.post(reverse('core:signup'), {
            'username': 'novouser',
            'password1': 'teste@123#Seguro',
            'password2': 'teste@123#Seguro',
        }, follow=True)
        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(any('sucesso' in str(m).lower() for m in messages))


class URLTest(TestCase):
    def test_home_url_resolve(self):
        resolver = resolve('/')
        self.assertEqual(resolver.func, views.home)

    def test_signup_url_resolve(self):
        resolver = resolve('/signup/')
        self.assertEqual(resolver.func, views.signup)

    def test_perfil_url_resolve(self):
        resolver = resolve('/perfil/')
        self.assertEqual(resolver.func, views.perfil)

    def test_perfil_url_name(self):
        self.assertEqual(reverse('core:perfil'), '/perfil/')

    def test_home_url_name(self):
        self.assertEqual(reverse('core:home'), '/')

    def test_signup_url_name(self):
        self.assertEqual(reverse('core:signup'), '/signup/')

    def test_excluir_url_resolve(self):
        resolver = resolve('/excluir/1/')
        self.assertEqual(resolver.func, views.excluir_registro)

    def test_excluir_url_name(self):
        self.assertEqual(
            reverse('core:excluir_registro', args=[1]),
            '/excluir/1/',
        )


class UserProfileModelTest(TestCase):
    def setUp(self):
        self.usuario = User.objects.create_user(username='testuser', password='12345')

    def test_profile_criado_automaticamente_ao_acessar(self):
        profile = UserProfile.objects.get_or_create(user=self.usuario)[0]
        self.assertEqual(profile.user, self.usuario)
        self.assertEqual(profile.tema, 'light')
        self.assertEqual(profile.paleta_cores, 'default')
        self.assertIsNone(profile.telefone)

    def test_profile_string_representation(self):
        profile = UserProfile.objects.get_or_create(user=self.usuario)[0]
        self.assertEqual(str(profile), f'Perfil de {self.usuario.username}')

    def test_profile_tema_e_paleta_personalizados(self):
        profile = UserProfile.objects.get_or_create(user=self.usuario)[0]
        profile.tema = 'dark'
        profile.paleta_cores = 'forest'
        profile.telefone = '(11) 99999-8888'
        profile.save()
        perfil_atualizado = UserProfile.objects.get(user=self.usuario)
        self.assertEqual(perfil_atualizado.tema, 'dark')
        self.assertEqual(perfil_atualizado.paleta_cores, 'forest')
        self.assertEqual(perfil_atualizado.telefone, '(11) 99999-8888')

    def test_profile_onetoone_unique(self):
        UserProfile.objects.create(user=self.usuario)
        with self.assertRaises(Exception):
            UserProfile.objects.create(user=self.usuario)


class SignupFormTest(TestCase):
    def test_signup_form_com_telefone(self):
        form = SignupForm(data={
            'username': 'novouser',
            'telefone': '(11) 91234-5678',
            'password1': 'Senha@Forte123',
            'password2': 'Senha@Forte123',
        })
        self.assertTrue(form.is_valid())

    def test_signup_form_sem_telefone(self):
        form = SignupForm(data={
            'username': 'novouser',
            'password1': 'Senha@Forte123',
            'password2': 'Senha@Forte123',
        })
        self.assertTrue(form.is_valid())

    def test_signup_form_salva_profile(self):
        form = SignupForm(data={
            'username': 'novouser',
            'telefone': '(11) 91234-5678',
            'password1': 'Senha@Forte123',
            'password2': 'Senha@Forte123',
        })
        self.assertTrue(form.is_valid())
        user = form.save()
        self.assertTrue(hasattr(user, 'profile'))
        self.assertEqual(user.profile.telefone, '(11) 91234-5678')

    def test_signup_form_senhas_nao_conferem(self):
        form = SignupForm(data={
            'username': 'novouser',
            'password1': 'Senha@Forte123',
            'password2': 'Senha@Diferente456',
        })
        self.assertFalse(form.is_valid())


class PerfilFormTest(TestCase):
    def setUp(self):
        self.usuario = User.objects.create_user(username='testuser', password='12345')
        self.profile = UserProfile.objects.create(user=self.usuario)

    def test_form_valido(self):
        form = PerfilForm(data={
            'telefone': '(21) 98765-4321',
            'tema': 'dark',
            'paleta_cores': 'ocean',
        }, instance=self.profile)
        self.assertTrue(form.is_valid())

    def test_form_atualiza_profile(self):
        form = PerfilForm(data={
            'telefone': '(21) 98765-4321',
            'tema': 'dark',
            'paleta_cores': 'ocean',
        }, instance=self.profile)
        self.assertTrue(form.is_valid())
        form.save()
        self.profile.refresh_from_db()
        self.assertEqual(self.profile.telefone, '(21) 98765-4321')
        self.assertEqual(self.profile.tema, 'dark')
        self.assertEqual(self.profile.paleta_cores, 'ocean')

    def test_valores_padrao_no_form(self):
        form = PerfilForm(instance=self.profile)
        self.assertEqual(form.initial['tema'], 'light')
        self.assertEqual(form.initial['paleta_cores'], 'default')


class PerfilViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.usuario = User.objects.create_user(username='testuser', password='12345')

    def test_redireciona_se_nao_autenticado(self):
        response = self.client.get(reverse('core:perfil'))
        self.assertEqual(response.status_code, 302)
        self.assertIn('/login/', response.url)

    def test_status_code_autenticado(self):
        self.client.login(username='testuser', password='12345')
        response = self.client.get(reverse('core:perfil'))
        self.assertEqual(response.status_code, 200)

    def test_template_usado(self):
        self.client.login(username='testuser', password='12345')
        response = self.client.get(reverse('core:perfil'))
        self.assertTemplateUsed(response, 'core/perfil.html')

    def test_context_contem_form(self):
        self.client.login(username='testuser', password='12345')
        response = self.client.get(reverse('core:perfil'))
        self.assertIn('form', response.context)

    def test_post_atualiza_perfil(self):
        self.client.login(username='testuser', password='12345')
        response = self.client.post(reverse('core:perfil'), {
            'telefone': '(31) 99876-5432',
            'tema': 'dark',
            'paleta_cores': 'forest',
        })
        self.assertEqual(response.status_code, 302)
        profile = UserProfile.objects.get(user=self.usuario)
        self.assertEqual(profile.telefone, '(31) 99876-5432')
        self.assertEqual(profile.tema, 'dark')
        self.assertEqual(profile.paleta_cores, 'forest')

    def test_mensagem_sucesso_perfil(self):
        self.client.login(username='testuser', password='12345')
        response = self.client.post(reverse('core:perfil'), {
            'telefone': '(31) 99876-5432',
            'tema': 'dark',
            'paleta_cores': 'forest',
        }, follow=True)
        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(any('atualizado' in str(m).lower() for m in messages))


